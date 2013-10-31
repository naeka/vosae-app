# -*- coding:Utf-8 -*-

from mongoengine import fields

from notification.models.invoicing_notifications.invoicing_notification import InvoicingNotification


__all__ = (
    'QuotationMakeInvoice',
    'QuotationMakeDownPaymentInvoice',
)


class QuotationMakeInvoice(InvoicingNotification):
    quotation = fields.ReferenceField("Quotation", required=True)
    invoice = fields.ReferenceField("Invoice", required=True)


class QuotationMakeDownPaymentInvoice(InvoicingNotification):
    quotation = fields.ReferenceField("Quotation", required=True)
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True)
