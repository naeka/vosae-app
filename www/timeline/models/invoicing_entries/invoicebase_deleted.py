# -*- coding:Utf-8 -*-

from mongoengine import fields

from timeline.models.invoicing_entries.invoicing_timeline_entry import InvoicingTimelineEntry


__all__ = (
    'QuotationDeleted',
    'PurchaseOrderDeleted',
    'InvoiceDeleted',
)


class QuotationDeleted(InvoicingTimelineEntry):
    quotation = fields.ReferenceField("Quotation", required=True)


class PurchaseOrderDeleted(InvoicingTimelineEntry):
    purchase_order = fields.ReferenceField("PurchaseOrder", required=True)


class InvoiceDeleted(InvoicingTimelineEntry):
    invoice = fields.ReferenceField("Invoice", required=True)
