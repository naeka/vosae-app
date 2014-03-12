# -*- coding:Utf-8 -*-

from django.template.defaultfilters import date as format_date
from django.utils.translation import ugettext as _
from reportlab.lib.units import mm

from invoicing.pdf.invoice_base import InvoiceBaseReport


__all__ = ('QuotationReport',)


class QuotationReport(InvoiceBaseReport):
    """Quotation documents report"""

    def __init__(self, report_settings, invoice_base, *args, **kwargs):
        from invoicing.models import Quotation
        if not isinstance(invoice_base, Quotation):
            raise TypeError('QuotationReport shoud receive an Quotation as invoice_base argument')
        super(InvoiceBaseReport, self).__init__(report_settings, *args, **kwargs)
        self.invoice_base = invoice_base

    def fill_description(self):
        """
        Fills the description:

        - Quotation reference
        - Dates
        - (Customer reference)
        """
        self.table([[
            ' '.join([unicode(self.invoice_base.RECORD_NAME).upper(), self.invoice_base.reference]),
            format_date(self.invoice_base.current_revision.quotation_date, 'DATE_FORMAT')
        ]], self.settings.page_size.scaled_width((120*mm, 50*mm)), style=self.style['InvoiceBaseReferencesTable'])

    def fill_legal_notice(self):
        # Legal notices
        if self.invoice_base.current_revision.quotation_validity:
            self.spacer()
            self.p(_("Valid until %(quotation_validity)s") % {
                'quotation_validity': format_date(self.invoice_base.current_revision.quotation_validity, 'DATE_FORMAT')
            })
        super(QuotationReport, self).fill_legal_notice()

    def fill_last_report_part(self):
        self.spacer()
        # Signature / stamp must have space available below
        self.start_keeptogether()
        self.p(_('Signature and stamp preceded by "Valid for agreement"'), self.style['Bold'])
        self.spacer(15*mm)
        self.end_keeptogether()
