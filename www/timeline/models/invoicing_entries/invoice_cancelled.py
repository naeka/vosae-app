# -*- coding:Utf-8 -*-

from mongoengine import fields

from timeline.models.invoicing_entries.invoicing_timeline_entry import InvoicingTimelineEntry


__all__ = (
    'InvoiceCancelled',
    'DownPaymentInvoiceCancelled',
)


class InvoiceCancelled(InvoicingTimelineEntry):
    invoice = fields.ReferenceField("Invoice", required=True)
    credit_note = fields.ReferenceField("CreditNote", required=True)


class DownPaymentInvoiceCancelled(InvoicingTimelineEntry):
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True)
    credit_note = fields.ReferenceField("CreditNote", required=True)
