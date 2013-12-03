# -*- coding:Utf-8 -*-

from mongoengine import fields

from notification.models.invoicing_notifications.invoicing_notification import InvoicingNotification


__all__ = (
    'QuotationChangedState',
    'PurchaseOrderChangedState',
    'InvoiceChangedState',
    'DownPaymentInvoiceChangedState',
    'CreditNoteChangedState',
)


class ChangedState(InvoicingNotification):
    previous_state = fields.StringField(required=True)
    new_state = fields.StringField(required=True)


class QuotationChangedState(ChangedState):
    quotation = fields.ReferenceField("Quotation", required=True)


class PurchaseOrderChangedState(ChangedState):
    purchase_order = fields.ReferenceField("PurchaseOrder", required=True)


class InvoiceChangedState(ChangedState):
    invoice = fields.ReferenceField("Invoice", required=True)


class DownPaymentInvoiceChangedState(ChangedState):
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True)


class CreditNoteChangedState(ChangedState):
    credit_note = fields.ReferenceField("CreditNote", required=True)
