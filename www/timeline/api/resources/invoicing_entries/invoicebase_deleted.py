# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from timeline.api.resources.base import TimelineEntryBaseResource
from timeline.api.doc import HELP_TEXT
from timeline.models import invoicing_entries


__all__ = (
    'QuotationDeletedResource',
    'PurchaseOrderDeletedResource',
    'InvoiceDeletedResource',
)


class QuotationDeletedResource(TimelineEntryBaseResource):
    quotation_reference = base_fields.CharField(
        attribute='quotation__reference',
        help_text=HELP_TEXT['invoicebase_deleted']['quotation'],
    )
    customer_display = base_fields.CharField(
        attribute='quotation__current_revision__get_customer_display',
        help_text=HELP_TEXT['invoicebase_deleted']['customer_display'],
        null=True
    )

    quotation = fields.ReferenceField(
        to='invoicing.api.resources.QuotationResource',
        attribute='quotation',
        help_text=HELP_TEXT['invoicebase_deleted']['quotation']
    )

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'quotation_deleted'
        object_class = invoicing_entries.QuotationDeleted


class PurchaseOrderDeletedResource(TimelineEntryBaseResource):
    purchase_order_reference = base_fields.CharField(
        attribute='purchase_order__reference',
        help_text=HELP_TEXT['invoicebase_deleted']['purchase_order_reference'],
    )
    customer_display = base_fields.CharField(
        attribute='purchase_order__current_revision__get_customer_display',
        help_text=HELP_TEXT['invoicebase_deleted']['customer_display'],
        null=True
    )

    purchase_order = fields.ReferenceField(
        to='invoicing.api.resources.PurchaseOrderResource',
        attribute='purchase_order',
        help_text=HELP_TEXT['invoicebase_deleted']['purchase_order']
    )

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'purchase_order_deleted'
        object_class = invoicing_entries.PurchaseOrderDeleted


class InvoiceDeletedResource(TimelineEntryBaseResource):
    invoice_reference = base_fields.CharField(
        attribute='invoice__reference',
        help_text=HELP_TEXT['invoicebase_deleted']['invoice'],
    )
    customer_display = base_fields.CharField(
        attribute='invoice__current_revision__get_customer_display',
        help_text=HELP_TEXT['invoicebase_deleted']['customer_display'],
        null=True
    )

    invoice = fields.ReferenceField(
        to='invoicing.api.resources.InvoiceResource',
        attribute='invoice',
        help_text=HELP_TEXT['invoicebase_deleted']['invoice']
    )

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'invoice_deleted'
        object_class = invoicing_entries.InvoiceDeleted
