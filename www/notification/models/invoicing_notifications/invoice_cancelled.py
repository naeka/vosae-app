# -*- coding:Utf-8 -*-

from mongoengine import fields

from notification.models.invoicing_notifications.invoicing_notification import InvoicingNotification


__all__ = (
    'InvoiceCancelled',
    'DownPaymentInvoiceCancelled',
)


class InvoiceCancelled(InvoicingNotification):
    invoice = fields.ReferenceField("Invoice", required=True)
    credit_note = fields.ReferenceField("CreditNote", required=True)


class DownPaymentInvoiceCancelled(InvoicingNotification):
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True)
    credit_note = fields.ReferenceField("CreditNote", required=True)
