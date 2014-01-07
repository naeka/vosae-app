# -*- coding:Utf-8 -*-

from mongoengine import fields

from notification.models.invoicing_notifications.invoicing_notification import InvoicingNotification


__all__ = (
    'QuotationMakeInvoice',
    'QuotationMakeDownPaymentInvoice',
    'PurchaseOrderMakeInvoice',
    'PurchaseOrderMakeDownPaymentInvoice',
)


class QuotationMakeInvoice(InvoicingNotification):
    quotation = fields.ReferenceField("Quotation", required=True)
    invoice = fields.ReferenceField("Invoice", required=True)


class QuotationMakeDownPaymentInvoice(InvoicingNotification):
    quotation = fields.ReferenceField("Quotation", required=True)
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True)


class PurchaseOrderMakeInvoice(InvoicingNotification):
    purchase_order = fields.ReferenceField("PurchaseOrder", required=True)
    invoice = fields.ReferenceField("Invoice", required=True)


class PurchaseOrderMakeDownPaymentInvoice(InvoicingNotification):
    purchase_order = fields.ReferenceField("PurchaseOrder", required=True)
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True)
