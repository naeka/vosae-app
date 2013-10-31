# -*- coding:Utf-8 -*-

from mongoengine import fields

from notification.models.invoicing_notifications.invoicing_notification import InvoicingNotification


__all__ = (
    'QuotationSaved',
    'InvoiceSaved',
    'DownPaymentInvoiceSaved',
    'CreditNoteSaved',
)


class QuotationSaved(InvoicingNotification):
    quotation = fields.ReferenceField("Quotation", required=True)


class InvoiceSaved(InvoicingNotification):
    invoice = fields.ReferenceField("Invoice", required=True)


class DownPaymentInvoiceSaved(InvoicingNotification):
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True)


class CreditNoteSaved(InvoicingNotification):
    credit_note = fields.ReferenceField("CreditNote", required=True)
