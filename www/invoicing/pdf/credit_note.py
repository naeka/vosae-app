# -*- coding:Utf-8 -*-

from django.template.defaultfilters import date as format_date
from django.utils.translation import ugettext as _
from reportlab.lib.units import mm

from invoicing.pdf.invoice_base import InvoiceBaseReport


__all__ = ('CreditNoteReport',)


class CreditNoteReport(InvoiceBaseReport):
    """CreditNote documents report"""

    def __init__(self, report_settings, invoice_base, *args, **kwargs):
        from invoicing.models import CreditNote
        if not isinstance(invoice_base, CreditNote):
            raise TypeError('CreditNoteReport shoud receive an CreditNote as invoice_base argument')
        super(InvoiceBaseReport, self).__init__(report_settings, *args, **kwargs)
        self.invoice_base = invoice_base

    def fill_description(self):
        """
        Fills the description:

        - Credit note reference
        - Dates
        - (Customer reference)
        """
        self.table([[
            ' '.join([unicode(self.invoice_base.RECORD_NAME).upper(), self.invoice_base.reference]),
            format_date(self.invoice_base.current_revision.credit_note_emission_date, 'DATE_FORMAT')
        ]], self.settings.page_size.scaled_width((120*mm, 50*mm)), style=self.style['InvoiceBaseReferencesTable'])

    def fill_legal_notice(self):
        # Legal notices
        self.spacer()
        self.p(_("Refers to invoice %(invoice_reference)s") % {
            'invoice_reference': self.invoice_base.related_to.reference
        })
        super(CreditNoteReport, self).fill_legal_notice()
