# -*- coding:Utf-8 -*-

from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from collections import OrderedDict
import csv
try:
    import cStringIO
    StringIO = cStringIO
except ImportError:
    import StringIO

from vosae_utils import IMEXSerializer
from invoicing.models import (
    Quotation,
    Invoice,
    CreditNote
)


__all__ = (
    'EXPORTABLE_DOCUMENTS_TYPES',
    'get_exportable_documents',
    'PDFSerializer',
    'QuotationCSVSerializer',
    'InvoiceCSVSerializer',
    'CreditNoteCSVSerializer',
)


EXPORTABLE_DOCUMENTS_TYPES = (
    'QUOTATION',
    'INVOICE',
    'CREDIT_NOTE'
)


def get_exportable_documents(export):
    documents = []
    if 'QUOTATION' in export.documents_types:
        full_export = Quotation.full_export(export.tenant, export.from_date, export.to_date)
        documents.append(full_export)
        serializer = QuotationCSVSerializer()
        documents.append((
            [serializer.serialize(full_export[0])],
            lambda buf: '{0}/{1}.csv'.format(_('Quotations'), _('Quotations')),
            lambda buf: buf
        ))

    if 'INVOICE' in export.documents_types:
        full_export = Invoice.full_export(export.tenant, export.from_date, export.to_date)
        documents.append(full_export)
        serializer = InvoiceCSVSerializer()
        documents.append((
            [serializer.serialize(full_export[0])],
            lambda buf: '{0}/{1}.csv'.format(_('Invoices'), _('Invoices')),
            lambda buf: buf
        ))

    if 'CREDIT_NOTE' in export.documents_types:
        full_export = CreditNote.full_export(export.tenant, export.from_date, export.to_date)
        documents.append(full_export)
        serializer = CreditNoteCSVSerializer()
        documents.append((
            [serializer.serialize(full_export[0])],
            lambda buf: '{0}/{1}.csv'.format(_('Credit notes'), _('Credit notes')),
            lambda buf: buf
        ))
    return documents


class PDFSerializer(IMEXSerializer):

    """
    PDF serializer
    """
    type_name = 'PDF'
    type_slug = 'pdf'
    type_mime = ('application/pdf',)
    type_ext = 'pdf'

    def serialize(self, invoicebase):
        pdf = invoicebase.get_pdf()
        return HttpResponseRedirect(pdf.download_link)


class InvoiceBaseCSVSerializer(IMEXSerializer):

    """
    Quotation CSV serializer
    """
    type_name = 'CSV'
    type_slug = 'csv'
    type_mime = ('text/csv',)
    type_ext = 'csv'

    def serialize(self, invoice_bases):
        self.csv_buffer = StringIO.StringIO()
        self.writer = csv.writer(self.csv_buffer)
        self.writer.writerow([k for k, v in self.fields])
        for invoice_base in invoice_bases:
            self._append_csv_row(invoice_base)
        return self.csv_buffer.getvalue()

    def _append_csv_row(self, invoice_base):
        """
        Append a serialized CSV row to buffer.
        """
        row_data = OrderedDict(self.fields)
        row_data.update(
            id=unicode(invoice_base.id),
            reference=invoice_base.reference,
            account_type=invoice_base.account_type,
            amount=invoice_base.amount,
            state=invoice_base.state,
            currency=invoice_base.current_revision.currency.symbol,
        )
        if invoice_base.current_revision.customer_reference:
            row_data['customer_reference'] = invoice_base.current_revision.customer_reference
        if invoice_base.organization:
            row_data['organization_id'] = unicode(invoice_base.organization.id)
        if invoice_base.contact:
            row_data['contact_id'] = unicode(invoice_base.contact.id)
        row_data.update(self._specific_fields_data(invoice_base))
        self.writer.writerow([unicode(s).encode('utf-8') for s in row_data.values()])

    def _specific_fields_data(self):
        return {}


class QuotationCSVSerializer(InvoiceBaseCSVSerializer):

    """
    Quotation CSV serializer
    """
    fields = (
        ('id', ''), ('reference', ''), ('account_type', ''), ('amount', ''),
        ('currency', ''), ('quotation_date', ''), ('organization_id', ''),
        ('contact_id', ''), ('state', ''), ('customer_reference', ''),
    )

    def _specific_fields_data(self, quotation):
        to_update = {}
        if quotation.current_revision.quotation_date:
            to_update.update(quotation_date=quotation.current_revision.quotation_date)
        return to_update


class InvoiceCSVSerializer(InvoiceBaseCSVSerializer):

    """
    Invoice CSV serializer
    """
    fields = (
        ('id', ''), ('reference', ''), ('account_type', ''), ('amount', ''),
        ('currency', ''), ('invoicing_date', ''), ('due_date', ''),
        ('organization_id', ''), ('contact_id', ''), ('state', ''),
        ('customer_reference', ''),
    )

    def _specific_fields_data(self, invoice):
        to_update = {}
        if invoice.current_revision.invoicing_date:
            to_update.update(invoicing_date=invoice.current_revision.invoicing_date)
        if invoice.current_revision.due_date:
            to_update.update(due_date=invoice.current_revision.due_date)
        return to_update


class CreditNoteCSVSerializer(InvoiceBaseCSVSerializer):

    """
    CreditNote CSV serializer
    """
    fields = (
        ('id', ''), ('reference', ''), ('account_type', ''), ('amount', ''),
        ('currency', ''), ('issue_date', ''), ('organization_id', ''),
        ('contact_id', ''), ('state', ''), ('customer_reference', ''),
    )

    def _specific_fields_data(self, credit_note):
        to_update = {}
        if credit_note.current_revision.issue_date:
            to_update.update(issue_date=credit_note.current_revision.issue_date)
        return to_update
