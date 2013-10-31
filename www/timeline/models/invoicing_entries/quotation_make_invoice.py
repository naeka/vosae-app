# -*- coding:Utf-8 -*-

from mongoengine import fields

from timeline.models.invoicing_entries.invoicing_timeline_entry import InvoicingTimelineEntry


__all__ = (
    'QuotationMakeInvoice',
    'QuotationMakeDownPaymentInvoice',
)


class QuotationMakeInvoice(InvoicingTimelineEntry):
    quotation = fields.ReferenceField("Quotation", required=True)
    invoice = fields.ReferenceField("Invoice", required=True)


class QuotationMakeDownPaymentInvoice(InvoicingTimelineEntry):
    quotation = fields.ReferenceField("Quotation", required=True)
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True)
