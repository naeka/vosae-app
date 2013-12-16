# -*- coding:Utf-8 -*-

from django.template.defaultfilters import date as format_date
from django.utils.translation import ugettext as _
from reportlab.lib.units import cm

from invoicing.pdf.invoice_base import InvoiceBaseReport


__all__ = ('PurchaseOrderReport',)


class PurchaseOrderReport(InvoiceBaseReport):
    """PurchaseOrder documents report"""

    def __init__(self, report_settings, invoice_base, *args, **kwargs):
        from invoicing.models import PurchaseOrder
        if not isinstance(invoice_base, PurchaseOrder):
            raise TypeError('PurchaseOrderReport shoud receive an PurchaseOrder as invoice_base argument')
        super(InvoiceBaseReport, self).__init__(report_settings, *args, **kwargs)
        self.invoice_base = invoice_base

    def fill_description(self):
        """
        Fills the description:

        - Purchase order reference
        - Dates
        - (Customer reference)
        """
        self.table([[
            ' '.join([unicode(self.invoice_base.RECORD_NAME).upper(), self.invoice_base.reference]),
            format_date(self.invoice_base.current_revision.purchase_order_date, 'DATE_FORMAT')
        ]], self.settings.page_size.scaled_width((12*cm, 5*cm)), style=self.style['InvoiceBaseReferencesTable'])

    def fill_legal_notice(self):
        # Legal notices
        if self.invoice_base.group.quotation:
            self.spacer()
            self.start_keeptogether()
            self.p(_("Refers to quotation %(quotation_reference)s") % {
                'quotation_reference': self.invoice_base.group.quotation.reference
            })
            self.end_keeptogether()
