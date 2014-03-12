# -*- coding:Utf-8 -*-

from django.template.defaultfilters import date as format_date
from django.utils.translation import ugettext as _, pgettext
from reportlab.lib.units import mm

from core.pdf.report import BaseTableStyle
from core.pdf.conf.fonts import get_font

from invoicing.pdf.invoice_base import InvoiceBaseReport
from invoicing import PAYMENT_TYPES, currency_format


__all__ = ('InvoiceReport',)


class InvoiceReport(InvoiceBaseReport):
    """Invoice documents report"""

    def __init__(self, report_settings, invoice_base, *args, **kwargs):
        from invoicing.models import Invoice
        if not isinstance(invoice_base, Invoice):
            raise TypeError('InvoiceReport shoud receive an Invoice as invoice_base argument')
        super(InvoiceBaseReport, self).__init__(report_settings, *args, **kwargs)
        self.invoice_base = invoice_base

    def fill_description(self):
        """
        Fills the description:

        - Invoice reference
        - Dates
        - (Customer reference)
        """
        reference = pgettext('reference', 'Undefined') if getattr(self.invoice_base, 'has_temporary_reference', None) else self.invoice_base.reference
        self.table([[
            ' '.join([unicode(self.invoice_base.RECORD_NAME).upper(), reference]),
            format_date(self.invoice_base.current_revision.invoicing_date, 'DATE_FORMAT')
        ]], self.settings.page_size.scaled_width((120*mm, 50*mm)), style=self.style['InvoiceBaseReferencesTable'])

    def fill_line_items_summary(self):
        """
        Fills line items summary table  
        Should start with a spacer
        """
        rows = self.get_line_items_summary_rows()
        # Position of the total row
        total_pos = len(rows) - 1
        custom_style = None

        # Add specific rows if there are linked down-payment invoices
        if self.invoice_base.is_invoice() and self.invoice_base.group.down_payment_invoices:
            for down_payment_invoice in self.invoice_base.group.down_payment_invoices:
                rows.append([
                    _('Down-payment invoice %(down_payment_invoice_reference)s') % {
                        'down_payment_invoice_reference': down_payment_invoice.reference
                    },
                    currency_format(down_payment_invoice.amount, down_payment_invoice.current_revision.currency.symbol)
                ])
            rows.append([
                _('NET PAYABLE'),
                currency_format(self.invoice_base.amount, self.invoice_base.current_revision.currency.symbol)
            ])
            custom_style = BaseTableStyle(
                name='InvoiceBaseSummaryTableWithDownPayments',
                parent=self.style['InvoiceBaseSummaryTable'],
                cmds=[
                    ('FONTNAME', (0, total_pos), (-1, total_pos), get_font(self.settings.font_name).bold),
                    ('FONTSIZE', (0, total_pos), (-1, total_pos), 1.2 * self.settings.font_size),
                    ('LEADING', (0, total_pos), (-1, total_pos), 1.5 * self.settings.font_size),
                    ('TEXTCOLOR', (0, total_pos), (-1, total_pos), self.settings.hex_font_base_color),
                    ('BACKGROUND', (0, total_pos), (-1, total_pos), self.settings.hex_base_color)
                ]
            )

        self.spacer()
        self.start_keeptogether()
        col_widths = (None, self.settings.page_size.scaled_width(25*mm))
        self.table(rows, col_widths, hAlign='RIGHT', style=custom_style or self.style['InvoiceBaseSummaryTable'])
        self.end_keeptogether()

    def fill_legal_notice(self):
        # Legal notices
        self.spacer()
        self.start_keeptogether()
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
        self.end_keeptogether()
        super(InvoiceReport, self).fill_legal_notice()
