# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext as _, pgettext
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Frame,
    PageTemplate,
    NextPageTemplate
)

from core.pdf.report import *
from core.pdf import colors
from invoicing import PAYMENT_TYPES

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class InvoiceBaseReport(Report):

    def __init__(self, report_settings, invoice_base, *args, **kwargs):
        from invoicing.models import InvoiceBase
        assert isinstance(invoice_base, InvoiceBase)
        super(InvoiceBaseReport, self).__init__(report_settings, *args, **kwargs)
        self.invoice_base = invoice_base

    def generate_templates(self):
        frame_kwargs = {
            # 'showBoundary': 1,
            'leftPadding': 0,
            'rightPadding': 0,
            'topPadding': 0,
            'bottomPadding': 0
        }
        address_frame_kwargs = frame_kwargs.copy()
        address_frame_kwargs.update(bottomPadding=2 * mm)

        sender_frame = NoSplitFrame(20 * mm, 260 * mm, 100 * mm, 25 * mm, **frame_kwargs)
        billing_frame = NoSplitFrame(20 * mm, 212 * mm, 75 * mm, 40 * mm, **address_frame_kwargs)
        shipping_frame = NoSplitFrame(115 * mm, 212 * mm, 75 * mm, 40 * mm, **address_frame_kwargs)
        rest_frame = Frame(20 * mm, 25 * mm, 170 * mm, 160 * mm, **frame_kwargs)
        full_frame = Frame(20 * mm, 25 * mm, 170 * mm, 247 * mm, **frame_kwargs)
        legal_notice_frame = NoSplitFrame(20 * mm, 5 * mm, 140 * mm, 11 * mm, **frame_kwargs)

        self.doc.addPageTemplates([
            PageTemplate(id='First', frames=[sender_frame, billing_frame, shipping_frame, rest_frame, legal_notice_frame], onPage=self.on_first_page_cb),
            PageTemplate(id='Other', frames=[full_frame, legal_notice_frame], onPage=self.on_other_pages_cb),
        ])
        self.story.append(NextPageTemplate('Other'))

    def generate_style(self):
        super(InvoiceBaseReport, self).generate_style()
        self.style.add(ParagraphStyle(
            name='Address',
            parent=self.style['Normal'],
            fontName='%s-Bold' % self.settings.font_name,
            fontSize=1.2 * self.settings.font_size,
            leading=1.45 * self.settings.font_size
        ))

        self.style.add(BaseTableStyle(
            name='InvoiceBaseReferencesTable',
            parent=self.style['ReportTable'],
            cmds=[
                ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, 0), 'BOTTOM'),
                ('FONTSIZE', (0, 0), (0, 0), 1.5 * self.settings.font_size),
                ('FONTSIZE', (-1, 0), (-1, 0), 1.2 * self.settings.font_size),
                ('LEADING', (0, 0), (0, 0), 2 * self.settings.font_size),
                ('LEADING', (-1, 0), (-1, 0), 1.5 * self.settings.font_size),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]
        ))

        self.style.add(BaseTableStyle(
            name='InvoiceBaseItemsTable',
            parent=self.style['ReportTable'],
            cmds=[
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ]
        ))

        self.style.add(BaseTableStyle(
            name='InvoiceBaseSummaryTable',
            parent=self.style['Table'],
            cmds=[
                ('FONTNAME', (0, -1), (-1, -1), '%s-Bold' % self.settings.font_name),
                ('FONTSIZE', (0, -1), (-1, -1), 1.2 * self.settings.font_size),
                ('LEADING', (0, -1), (-1, -1), 1.5 * self.settings.font_size),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('TEXTCOLOR', (-2, -1), (-1, -1), colors.white),
                ('BACKGROUND', (-1, 0), (-1, -1), colors.grey),
                ('BACKGROUND', (-2, -1), (-1, -1), colors.green),
                ('LINEBELOW', (0, 0), (-1, -2), 4, colors.white),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -2), 6),
            ]
        ))

    def on_first_page_cb(self, canvas, document):
        super(InvoiceBaseReport, self).on_first_page_cb(canvas, document)
        # Main line
        canvas.saveState()
        canvas.setLineWidth(1.5 * mm)
        canvas.setLineCap(1)
        canvas.setStrokeColor(colors.darkgrey)
        canvas.line(20 * mm, 193 * mm, 190 * mm, 193 * mm)
        canvas.restoreState()

        # Addresses labels
        canvas.saveState()
        canvas.setLineWidth(0.2)
        canvas.setLineCap(1)
        canvas.setStrokeColor(colors.green)
        canvas.setFont('%s' % self.settings.font_name, 9)
        canvas.setFillColor(colors.green)
        canvas.line(20 * mm, 212 * mm, 95 * mm, 212 * mm)
        canvas.line(115 * mm, 212 * mm, 190 * mm, 212 * mm)
        canvas.drawString(20 * mm, 208 * mm, _("Billing address").upper())
        canvas.drawString(115 * mm, 208 * mm, _("Delivery address").upper())
        canvas.restoreState()

    def fill(self):
        from django.template.defaultfilters import date as format_date, floatformat
        from reportlab.platypus.flowables import Image
        from core.pdf.utils import Paragraph
        from invoicing import currency_format

        # Sender frame
        # Sender identity
        sender_paragraphs = []
        if self.invoice_base.current_revision.sender:
            sender_paragraphs.append(Paragraph(self.invoice_base.current_revision.sender, self.style['Small']))
        sender_paragraphs.append(Paragraph(self.invoice_base.tenant.name, self.style['Small']))
        if self.invoice_base.current_revision.sender_address:
            sender_paragraphs.append(Paragraph(u'\n'.join(self.invoice_base.current_revision.sender_address.get_formatted()), self.style['Small']))
        # Add layout table if logo or paragraphs
        if self.invoice_base.tenant.logo_cache:
            logo = Image(self.invoice_base.tenant.logo_cache)
            logo_width, logo_height = logo._restrictSize(50 * mm, 20 * mm)
            self.table(
                [[logo, sender_paragraphs]],
                (logo_width + 4 * mm, None),
                self.style['LayoutTable'],
                rowHeights=(20 * mm,)
            )
        else:
            for paragraph in sender_paragraphs:
                self.append(paragraph)

        # Billing address frame
        self.next_frame()
        if self.invoice_base.current_revision.contact:
            self.p(self.invoice_base.current_revision.contact.get_full_name(upper_name=True), style=self.style['Address'])
        if self.invoice_base.current_revision.organization:
            self.p(self.invoice_base.current_revision.organization.corporate_name, style=self.style['Address'])
        if self.invoice_base.current_revision.billing_address:
            self.p(u'\n'.join(self.invoice_base.current_revision.billing_address.get_formatted()), style=self.style['Address'])

        # Delivery address frame
        self.next_frame()
        if self.invoice_base.current_revision.contact:
            self.p(self.invoice_base.current_revision.contact.get_full_name(upper_name=True), style=self.style['Address'])
        if self.invoice_base.current_revision.organization:
            self.p(self.invoice_base.current_revision.organization.corporate_name, style=self.style['Address'])
        if self.invoice_base.current_revision.delivery_address:
            self.p(u'\n'.join(self.invoice_base.current_revision.delivery_address.get_formatted()), style=self.style['Address'])

        # Rest of the report
        self.next_frame()
        invoice_reference = pgettext('date', 'Undefined') if getattr(self.invoice_base, 'has_temporary_reference', None) else self.invoice_base.reference
        self.table([[
            ' '.join([unicode(self.invoice_base.RECORD_NAME).upper(), invoice_reference]),
            format_date(self.invoice_base.current_revision.invoicing_date, 'DATE_FORMAT')
        ]], (12 * cm, 5 * cm), style=self.style['InvoiceBaseReferencesTable'])

        self.spacer()
        rows = [[
            pgettext('table-headers', 'Description'),
            pgettext('table-headers', 'Qty'),
            pgettext('table-headers', 'Unit price (excl. tax)'),
            pgettext('table-headers', 'Tax'),
            pgettext('table-headers', 'Total (excl. tax)')
        ]]
        for item in self.invoice_base.current_revision.line_items:
            rows.append([
                item.description,
                floatformat(item.quantity, -2),
                currency_format(item.unit_price),
                '{0:.2%}'.format(item.tax.rate),
                currency_format(item.total_price, self.invoice_base.current_revision.currency.symbol)
            ])
        col_widths = (85 * mm, 20 * mm, 20 * mm, 20 * mm, 25 * mm)
        self.table(rows, col_widths, repeatRows=1, style=self.style['InvoiceBaseItemsTable'])

        self.spacer()
        rows = [[
            _('TOTAL (excl. tax)'),
            currency_format(self.invoice_base.sub_total, self.invoice_base.current_revision.currency.symbol)
        ]]
        for tax in self.invoice_base.taxes_amounts:
            rows.append([
                '%(tax_name)s (%(tax_rate)s)' % {
                    'tax_name': tax.get('name'),
                    'tax_rate': '{0:.2%}'.format(tax.get('rate'))
                },
                currency_format(tax.get('amount'), self.invoice_base.current_revision.currency.symbol)
            ])
        rows.append([
            _('TOTAL (incl. tax)'),
            currency_format(self.invoice_base.amount, self.invoice_base.current_revision.currency.symbol)
        ])
        col_widths = (None, 25 * mm)
        self.start_keeptogether()
        self.table(rows, col_widths, hAlign='RIGHT', style=self.style['InvoiceBaseSummaryTable'])
        self.end_keeptogether()

        # Legal notices
        self.spacer()
        self.start_keeptogether()
        if self.invoice_base.is_quotation():
            self.p(_("Valid until %(quotation_validity)s") % {
                'quotation_validity': format_date(self.invoice_base.current_revision.quotation_validity, 'DATE_FORMAT')
            })
        elif self.invoice_base.is_purchase_order():
            if self.invoice_base.group.quotation:
                self.p(_("Refers to quotation %(quotation_reference)s") % {
                    'quotation_reference': self.invoice_base.group.quotation.reference
                })
            else:
                self.p('')
        elif self.invoice_base.is_invoice() or self.invoice_base.is_down_payment_invoice():
            if self.invoice_base.current_revision.custom_payment_conditions:
                self.p(_("Payment conditions: %(custom_payment_conditions)s") % {
                    'custom_payment_conditions': self.invoice_base.current_revision.custom_payment_conditions
                })
            else:
                self.p(_("Payment due date on %(due_date)s") % {
                    'due_date': format_date(self.invoice_base.current_revision.due_date, 'DATE_FORMAT')
                })
            pt_dict = dict(PAYMENT_TYPES)
            invoicing_settings = self.invoice_base.tenant.tenant_settings.invoicing
            self.p(_("Accepted payment methods: %(accepted_payment_methods)s") % {
                'accepted_payment_methods': u', '.join([unicode(pt_dict.get(pt, pt)).lower() for pt in invoicing_settings.accepted_payment_types])
            })
            if invoicing_settings.late_fee_rate:
                self.p(_("Late fee rate: %(late_fee_rate)s") % {
                    'late_fee_rate': u'{0:.2%}'.format(invoicing_settings.late_fee_rate)
                })
            else:
                self.p(_("Late fee at the legal rate"))
        elif self.invoice_base.is_credit_note():
            self.p(_("Refers to invoice %(invoice_reference)s") % {
                'invoice_reference': self.invoice_base.group.invoice.reference
            })
        else:
            self.p('')
        self.end_keeptogether()

        # Registration information
        self.next_frame()
        registration_info_parts = [self.invoice_base.tenant.name] + self.invoice_base.tenant.registration_info.get_list()
        self.p(u' - '.join(registration_info_parts), style=self.style['Smaller'])

        # Metadata
        if self.invoice_base.issuer:
            self.doc.author = self.invoice_base.issuer.get_full_name()
        if self.invoice_base.reference:
            document_name = ' '.join([
                unicode(self.invoice_base.RECORD_NAME).upper(),
                self.invoice_base.reference
            ])
            self.doc.title = document_name
            self.doc.subject = document_name
        self.doc.creator = self.invoice_base.tenant.name
        self.doc.keywords = self.invoice_base.keywords
