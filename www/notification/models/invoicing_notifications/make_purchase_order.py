# -*- coding:Utf-8 -*-

from mongoengine import fields

from notification.models.invoicing_notifications.invoicing_notification import InvoicingNotification


__all__ = (
    'QuotationMakePurchaseOrder',
)


class QuotationMakePurchaseOrder(InvoicingNotification):
    quotation = fields.ReferenceField("Quotation", required=True)
    purchase_order = fields.ReferenceField("PurchaseOrder", required=True)
