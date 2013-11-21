# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from timeline.api.resources.base import TimelineEntryBaseResource
from timeline.api.doc import HELP_TEXT
from timeline.models import invoicing_entries


__all__ = (
    'QuotationMakeInvoiceResource',
    'QuotationMakeDownPaymentInvoiceResource',
    'PurchaseOrderMakeInvoiceResource',
    'PurchaseOrderMakeDownPaymentInvoiceResource',
)


class QuotationMakeInvoiceResource(TimelineEntryBaseResource):
    quotation_reference = base_fields.CharField(
        attribute='quotation__reference',
        help_text=HELP_TEXT['quotation_make_invoice']['quotation_reference'],
    )
    invoice_reference = base_fields.CharField(
        attribute='invoice__reference',
        help_text=HELP_TEXT['quotation_make_invoice']['invoice_reference'],
    )
    customer_display = base_fields.CharField(
        attribute='invoice__current_revision__get_customer_display',
        help_text=HELP_TEXT['quotation_make_invoice']['customer_display'],
        null=True
    )
    invoice_has_temporary_reference = base_fields.BooleanField(
        attribute='invoice__has_temporary_reference',
        help_text=HELP_TEXT['quotation_make_invoice']['has_temporary_reference'],
    )

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

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'quotation_make_invoice'
        object_class = invoicing_entries.QuotationMakeInvoice


class QuotationMakeDownPaymentInvoiceResource(TimelineEntryBaseResource):
    quotation_reference = base_fields.CharField(
        attribute='quotation__reference',
        help_text=HELP_TEXT['quotation_make_invoice']['quotation_reference'],
    )
    down_payment_invoice_reference = base_fields.CharField(
        attribute='down_payment_invoice__reference',
        help_text=HELP_TEXT['quotation_make_down_payment_invoice']['down_payment_invoice_reference'],
    )
    customer_display = base_fields.CharField(
        attribute='invoice__current_revision__get_customer_display',
        help_text=HELP_TEXT['quotation_make_invoice']['customer_display'],
        null=True
    )

    quotation = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='quotation',
        help_text=HELP_TEXT['quotation_make_invoice']['quotation']
    )
    down_payment_invoice = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='down_payment_invoice',
        help_text=HELP_TEXT['quotation_make_down_payment_invoice']['down_payment_invoice']
    )

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'quotation_make_down_payment_invoice'
        object_class = invoicing_entries.QuotationMakeDownPaymentInvoice


class PurchaseOrderMakeInvoiceResource(TimelineEntryBaseResource):
    purchase_order_reference = base_fields.CharField(
        attribute='purchase_order__reference',
        help_text=HELP_TEXT['purchase_order_make_invoice']['purchase_order_reference'],
    )
    invoice_reference = base_fields.CharField(
        attribute='invoice__reference',
        help_text=HELP_TEXT['purchase_order_make_invoice']['invoice_reference'],
    )
    customer_display = base_fields.CharField(
        attribute='invoice__current_revision__get_customer_display',
        help_text=HELP_TEXT['purchase_order_make_invoice']['customer_display'],
        null=True
    )
    invoice_has_temporary_reference = base_fields.BooleanField(
        attribute='invoice__has_temporary_reference',
        help_text=HELP_TEXT['purchase_order_make_invoice']['has_temporary_reference'],
    )

    purchase_order = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='purchase_order',
        help_text=HELP_TEXT['purchase_order_make_invoice']['purchase_order']
    )
    invoice = fields.ReferenceField(
        to='invoicing.api.resources.InvoiceResource',
        attribute='invoice',
        help_text=HELP_TEXT['purchase_order_make_invoice']['invoice']
    )

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'purchase_order_make_invoice'
        object_class = invoicing_entries.PurchaseOrderMakeInvoice


class PurchaseOrderMakeDownPaymentInvoiceResource(TimelineEntryBaseResource):
    purchase_order_reference = base_fields.CharField(
        attribute='purchase_order__reference',
        help_text=HELP_TEXT['purchase_order_make_invoice']['purchase_order_reference'],
    )
    down_payment_invoice_reference = base_fields.CharField(
        attribute='down_payment_invoice__reference',
        help_text=HELP_TEXT['purchase_order_make_down_payment_invoice']['down_payment_invoice_reference'],
    )
    customer_display = base_fields.CharField(
        attribute='invoice__current_revision__get_customer_display',
        help_text=HELP_TEXT['purchase_order_make_invoice']['customer_display'],
        null=True
    )

    purchase_order = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='purchase_order',
        help_text=HELP_TEXT['purchase_order_make_invoice']['purchase_order']
    )
    down_payment_invoice = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='down_payment_invoice',
        help_text=HELP_TEXT['purchase_order_make_down_payment_invoice']['down_payment_invoice']
    )

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'purchase_order_make_down_payment_invoice'
        object_class = invoicing_entries.PurchaseOrderMakeDownPaymentInvoice
