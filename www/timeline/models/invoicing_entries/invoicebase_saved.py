# -*- coding:Utf-8 -*-

from mongoengine import fields

from timeline.models.invoicing_entries.invoicing_timeline_entry import InvoicingTimelineEntry


__all__ = (
    'QuotationSaved',
    'PurchaseOrderSaved',
    'InvoiceSaved',
    'DownPaymentInvoiceSaved',
    'CreditNoteSaved',
)


class Saved(InvoicingTimelineEntry):
    created = fields.BooleanField(required=True)


class QuotationSaved(Saved):
    quotation = fields.ReferenceField("Quotation", required=True)


class PurchaseOrderSaved(Saved):
    purchase_order = fields.ReferenceField("PurchaseOrder", required=True)


class InvoiceSaved(Saved):
    invoice = fields.ReferenceField("Invoice", required=True)


class DownPaymentInvoiceSaved(Saved):
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True)


class CreditNoteSaved(Saved):
    credit_note = fields.ReferenceField("CreditNote", required=True)
