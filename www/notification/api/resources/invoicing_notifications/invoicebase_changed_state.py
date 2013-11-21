# -*- coding:Utf-8 -*-

from tastypie_mongoengine import fields

from notification.api.resources.base import NotificationBaseResource
from notification.api.doc import HELP_TEXT
from notification.models import invoicing_notifications


__all__ = (
    'QuotationChangedStateResource',
    'PurchaseOrderChangedStateResource',
    'InvoiceChangedStateResource',
    'DownPaymentInvoiceChangedStateResource',
    'CreditNoteChangedStateResource',
)


class QuotationChangedStateResource(NotificationBaseResource):
    quotation = fields.ReferenceField(
        to='invoicing.api.resources.QuotationResource',
        attribute='quotation',
        help_text=HELP_TEXT['invoicebase_changed_state']['quotation']
    )

    class Meta(NotificationBaseResource.Meta):
        resource_name = 'quotation_changed_state'
        object_class = invoicing_notifications.QuotationChangedState


class PurchaseOrderChangedStateResource(NotificationBaseResource):
    purchase_order = fields.ReferenceField(
        to='invoicing.api.resources.PurchaseOrderResource',
        attribute='purchase_order',
        help_text=HELP_TEXT['invoicebase_changed_state']['purchase_order']
    )

    class Meta(NotificationBaseResource.Meta):
        resource_name = 'purchase_order_changed_state'
        object_class = invoicing_notifications.PurchaseOrderChangedState


class InvoiceChangedStateResource(NotificationBaseResource):
    invoice = fields.ReferenceField(
        to='invoicing.api.resources.InvoiceResource',
        attribute='invoice',
        help_text=HELP_TEXT['invoicebase_changed_state']['invoice']
    )

    class Meta(NotificationBaseResource.Meta):
        resource_name = 'invoice_changed_state'
        object_class = invoicing_notifications.InvoiceChangedState


class DownPaymentInvoiceChangedStateResource(NotificationBaseResource):
    down_payment_invoice = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='down_payment_invoice',
        help_text=HELP_TEXT['invoicebase_changed_state']['down_payment_invoice']
    )

    class Meta(NotificationBaseResource.Meta):
        resource_name = 'down_payment_invoice_changed_state'
        object_class = invoicing_notifications.DownPaymentInvoiceChangedState


class CreditNoteChangedStateResource(NotificationBaseResource):
    credit_note = fields.ReferenceField(
        to='invoicing.api.resources.CreditNoteResource',
        attribute='credit_note',
        help_text=HELP_TEXT['invoicebase_changed_state']['credit_note']
    )

    class Meta(NotificationBaseResource.Meta):
        resource_name = 'credit_note_changed_state'
        object_class = invoicing_notifications.CreditNoteChangedState
