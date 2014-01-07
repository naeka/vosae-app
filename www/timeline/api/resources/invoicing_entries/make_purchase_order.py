# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from timeline.api.resources.base import TimelineEntryBaseResource
from timeline.api.doc import HELP_TEXT
from timeline.models import invoicing_entries


__all__ = (
    'QuotationMakePurchaseOrderResource',
)


class QuotationMakePurchaseOrderResource(TimelineEntryBaseResource):
    quotation_reference = base_fields.CharField(
        attribute='quotation__reference',
        help_text=HELP_TEXT['quotation_make_purchase_order']['quotation_reference'],
    )
    purchase_order_reference = base_fields.CharField(
        attribute='purchase_order__reference',
        help_text=HELP_TEXT['quotation_make_purchase_order']['purchase_order_reference'],
    )
    customer_display = base_fields.CharField(
        attribute='purchase_order__current_revision__get_customer_display',
        help_text=HELP_TEXT['quotation_make_purchase_order']['customer_display'],
        null=True
    )

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

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'quotation_make_purchase_order'
        object_class = invoicing_entries.QuotationMakePurchaseOrder
