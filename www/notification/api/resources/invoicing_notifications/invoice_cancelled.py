# -*- coding:Utf-8 -*-

from tastypie_mongoengine import fields

from notification.api.resources.base import NotificationBaseResource
from notification.api.doc import HELP_TEXT
from notification.models import invoicing_notifications


__all__ = (
    'InvoiceCancelledResource',
    'DownPaymentInvoiceCancelledResource',
)


class InvoiceCancelledResource(NotificationBaseResource):
    invoice = fields.ReferenceField(
        to='invoicing.api.resources.InvoiceResource',
        attribute='invoice',
        help_text=HELP_TEXT['invoice_cancelled']['invoice']
    )
    credit_note = fields.ReferenceField(
        to='invoicing.api.resources.CreditNoteResource',
        attribute='credit_note',
        help_text=HELP_TEXT['invoice_cancelled']['credit_note']
    )

    class Meta(NotificationBaseResource.Meta):
        resource_name = 'invoice_cancelled'
        object_class = invoicing_notifications.InvoiceCancelled


class DownPaymentInvoiceCancelledResource(NotificationBaseResource):
    down_payment_invoice = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='down_payment_invoice',
        help_text=HELP_TEXT['invoice_cancelled']['down_payment_invoice']
    )
    credit_note = fields.ReferenceField(
        to='invoicing.api.resources.CreditNoteResource',
        attribute='credit_note',
        help_text=HELP_TEXT['invoice_cancelled']['credit_note']
    )

    class Meta(NotificationBaseResource.Meta):
        resource_name = 'down_payment_invoice_cancelled'
        object_class = invoicing_notifications.DownPaymentInvoiceCancelled
