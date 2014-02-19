# -*- coding:Utf-8 -*-

from mongoengine import fields

from notification.models.invoicing_notifications.invoicing_notification import InvoicingNotification


__all__ = (
    'QuotationDeleted',
    'PurchaseOrderDeleted',
    'InvoiceDeleted',
)


class QuotationDeleted(InvoicingNotification):
    quotation = fields.ReferenceField("Quotation", required=True)


class PurchaseOrderDeleted(InvoicingNotification):
    purchase_order = fields.ReferenceField("PurchaseOrder", required=True)


class InvoiceDeleted(InvoicingNotification):
    invoice = fields.ReferenceField("Invoice", required=True)
