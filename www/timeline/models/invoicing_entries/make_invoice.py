# -*- coding:Utf-8 -*-

from mongoengine import fields

from timeline.models.invoicing_entries.invoicing_timeline_entry import InvoicingTimelineEntry


__all__ = (
    'QuotationMakeInvoice',
    'QuotationMakeDownPaymentInvoice',
    'PurchaseOrderMakeInvoice',
    'PurchaseOrderMakeDownPaymentInvoice',
)


class QuotationMakeInvoice(InvoicingTimelineEntry):
    quotation = fields.ReferenceField("Quotation", required=True)
    invoice = fields.ReferenceField("Invoice", required=True)


class QuotationMakeDownPaymentInvoice(InvoicingTimelineEntry):
    quotation = fields.ReferenceField("Quotation", required=True)
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True)


class PurchaseOrderMakeInvoice(InvoicingTimelineEntry):
    purchase_order = fields.ReferenceField("PurchaseOrder", required=True)
    invoice = fields.ReferenceField("Invoice", required=True)


class PurchaseOrderMakeDownPaymentInvoice(InvoicingTimelineEntry):
    purchase_order = fields.ReferenceField("PurchaseOrder", required=True)
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True)
