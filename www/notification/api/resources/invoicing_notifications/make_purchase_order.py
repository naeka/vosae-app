# -*- coding:Utf-8 -*-

from tastypie_mongoengine import fields

from notification.api.resources.base import NotificationBaseResource
from notification.api.doc import HELP_TEXT
from notification.models import invoicing_notifications


__all__ = (
    'QuotationMakePurchaseOrderResource',
)


class QuotationMakePurchaseOrderResource(NotificationBaseResource):
    quotation = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='quotation',
        help_text=HELP_TEXT['quotation_make_purchase_order']['quotation']
    )
    purchase_order = fields.ReferenceField(
        to='invoicing.api.resources.InvoiceResource',
        attribute='purchase_order',
        help_text=HELP_TEXT['quotation_make_purchase_order']['purchase_order']
    )

    class Meta(NotificationBaseResource.Meta):
        resource_name = 'quotation_make_purchase_order'
        object_class = invoicing_notifications.QuotationMakePurchaseOrder