# -*- coding:Utf-8 -*-

from mongoengine import fields

from timeline.models.invoicing_entries.invoicing_timeline_entry import InvoicingTimelineEntry


__all__ = (
    'QuotationAddedAttachment',
    'PurchaseOrderAddedAttachment',
    'InvoiceAddedAttachment',
    'DownPaymentInvoiceAddedAttachment',
    'CreditNoteAddedAttachment',
)


class AddedAttachment(InvoicingTimelineEntry):
    vosae_file = fields.ReferenceField("VosaeFile", required=True)


class QuotationAddedAttachment(AddedAttachment):
    quotation = fields.ReferenceField("Quotation", required=True)


class PurchaseOrderAddedAttachment(AddedAttachment):
    purchase_order = fields.ReferenceField("PurchaseOrder", required=True)


class InvoiceAddedAttachment(AddedAttachment):
    invoice = fields.ReferenceField("Invoice", required=True)


class DownPaymentInvoiceAddedAttachment(AddedAttachment):
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True)


class CreditNoteAddedAttachment(AddedAttachment):
    credit_note = fields.ReferenceField("CreditNote", required=True)
