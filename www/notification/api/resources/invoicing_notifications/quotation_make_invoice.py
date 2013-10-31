# -*- coding:Utf-8 -*-

from tastypie_mongoengine import fields

from notification.api.resources.base import NotificationBaseResource
from notification.api.doc import HELP_TEXT
from notification.models import invoicing_notifications


__all__ = (
    'QuotationMakeInvoiceResource',
    'QuotationMakeDownPaymentInvoiceResource',
)


class QuotationMakeInvoiceResource(NotificationBaseResource):
    quotation = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='quotation',
        help_text=HELP_TEXT['quotation_make_invoice']['quotation']
    )
    invoice = fields.ReferenceField(
        to='invoicing.api.resources.InvoiceResource',
        attribute='invoice',
        help_text=HELP_TEXT['quotation_make_invoice']['invoice']
    )

    class Meta(NotificationBaseResource.Meta):
        resource_name = 'quotation_make_invoice'
        object_class = invoicing_notifications.QuotationMakeInvoice


class QuotationMakeDownPaymentInvoiceResource(NotificationBaseResource):
    quotation = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='quotation',
        help_text=HELP_TEXT['quotation_make_invoice']['quotation']
    )
    down_payment_invoice = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='down_payment_invoice',
        help_text=HELP_TEXT['quotation_make_invoice']['down_payment_invoice']
    )

    class Meta(NotificationBaseResource.Meta):
        resource_name = 'quotation_make_down_payment_invoice'
        object_class = invoicing_notifications.QuotationMakeDownPaymentInvoice
