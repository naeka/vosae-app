# -*- coding:Utf-8 -*-

from mongoengine import fields

from notification.models.invoicing_notifications.invoicing_notification import InvoicingNotification


__all__ = (
    'QuotationAddedAttachment',
    'InvoiceAddedAttachment',
    'DownPaymentInvoiceAddedAttachment',
    'CreditNoteAddedAttachment',
)


class AddedAttachment(InvoicingNotification):
    vosae_file = fields.ReferenceField("VosaeFile", required=True)


class QuotationAddedAttachment(AddedAttachment):
    quotation = fields.ReferenceField("Quotation", required=True)


class InvoiceAddedAttachment(AddedAttachment):
    invoice = fields.ReferenceField("Invoice", required=True)


class DownPaymentInvoiceAddedAttachment(AddedAttachment):
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True)


class CreditNoteAddedAttachment(AddedAttachment):
    credit_note = fields.ReferenceField("CreditNote", required=True)
