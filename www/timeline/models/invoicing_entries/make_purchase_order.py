# -*- coding:Utf-8 -*-

from mongoengine import fields

from timeline.models.invoicing_entries.invoicing_timeline_entry import InvoicingTimelineEntry


__all__ = (
    'QuotationMakePurchaseOrder',
)


class QuotationMakePurchaseOrder(InvoicingTimelineEntry):
    quotation = fields.ReferenceField("Quotation", required=True)
    purchase_order = fields.ReferenceField("PurchaseOrder", required=True)
