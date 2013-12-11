# -*- coding:Utf-8 -*-

from django.template.defaultfilters import date as format_date
from django.utils.translation import ugettext as _, pgettext
from reportlab.lib.units import cm

from invoicing.pdf.invoice_base import InvoiceBaseReport
from invoicing import PAYMENT_TYPES


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
        ]], self.settings.page_size.scaled_width((12*cm, 5*cm)), style=self.style['InvoiceBaseReferencesTable'])

    def fill_legal_notice(self):
        # Legal notices
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
