# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from timeline.api.resources.base import TimelineEntryBaseResource
from timeline.api.doc import HELP_TEXT
from timeline.models import invoicing_entries


__all__ = (
    'QuotationSavedResource',
    'PurchaseOrderSavedResource',
    'InvoiceSavedResource',
    'DownPaymentInvoiceSavedResource',
    'CreditNoteSavedResource',
)


class QuotationSavedResource(TimelineEntryBaseResource):
    quotation_reference = base_fields.CharField(
        attribute='quotation__reference',
        help_text=HELP_TEXT['invoicebase_saved']['quotation'],
    )
    customer_display = base_fields.CharField(
        attribute='quotation__current_revision__get_customer_display',
        help_text=HELP_TEXT['invoicebase_saved']['customer_display'],
        null=True
    )

    quotation = fields.ReferenceField(
        to='invoicing.api.resources.QuotationResource',
        attribute='quotation',
        help_text=HELP_TEXT['invoicebase_saved']['quotation']
    )

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'quotation_saved'
        object_class = invoicing_entries.QuotationSaved


class PurchaseOrderSavedResource(TimelineEntryBaseResource):
    purchase_order_reference = base_fields.CharField(
        attribute='purchase_order__reference',
        help_text=HELP_TEXT['invoicebase_saved']['purchase_order_reference'],
    )
    customer_display = base_fields.CharField(
        attribute='purchase_order__current_revision__get_customer_display',
        help_text=HELP_TEXT['invoicebase_saved']['customer_display'],
        null=True
    )

    purchase_order = fields.ReferenceField(
        to='invoicing.api.resources.PurchaseOrderResource',
        attribute='purchase_order',
        help_text=HELP_TEXT['invoicebase_saved']['purchase_order']
    )

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'purchase_order_saved'
        object_class = invoicing_entries.PurchaseOrderSaved


class InvoiceSavedResource(TimelineEntryBaseResource):
    invoice_reference = base_fields.CharField(
        attribute='invoice__reference',
        help_text=HELP_TEXT['invoicebase_saved']['invoice'],
    )
    invoice_has_temporary_reference = base_fields.BooleanField(
        attribute='invoice__has_temporary_reference',
        help_text=HELP_TEXT['invoicebase_saved']['has_temporary_reference'],
    )
    customer_display = base_fields.CharField(
        attribute='invoice__current_revision__get_customer_display',
        help_text=HELP_TEXT['invoicebase_saved']['customer_display'],
        null=True
    )

    invoice = fields.ReferenceField(
        to='invoicing.api.resources.InvoiceResource',
        attribute='invoice',
        help_text=HELP_TEXT['invoicebase_saved']['invoice']
    )

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'invoice_saved'
        object_class = invoicing_entries.InvoiceSaved


class DownPaymentInvoiceSavedResource(TimelineEntryBaseResource):
    down_payment_invoice_reference = base_fields.CharField(
        attribute='down_payment_invoice__reference',
        help_text=HELP_TEXT['invoicebase_saved']['down_payment_invoice'],
    )
    customer_display = base_fields.CharField(
        attribute='down_payment_invoice__current_revision__get_customer_display',
        help_text=HELP_TEXT['invoicebase_saved']['customer_display'],
        null=True
    )

    down_payment_invoice = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='down_payment_invoice',
        help_text=HELP_TEXT['invoicebase_saved']['down_payment_invoice']
    )

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'down_payment_invoice_saved'
        object_class = invoicing_entries.DownPaymentInvoiceSaved


class CreditNoteSavedResource(TimelineEntryBaseResource):
    credit_note_reference = base_fields.CharField(
        attribute='credit_note__reference',
        help_text=HELP_TEXT['invoicebase_saved']['credit_note'],
    )
    customer_display = base_fields.CharField(
        attribute='credit_note__current_revision__get_customer_display',
        help_text=HELP_TEXT['invoicebase_saved']['customer_display'],
        null=True
    )

    credit_note = fields.ReferenceField(
        to='invoicing.api.resources.CreditNoteResource',
        attribute='credit_note',
        help_text=HELP_TEXT['invoicebase_saved']['credit_note']
    )

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'credit_note_saved'
        object_class = invoicing_entries.CreditNoteSaved
