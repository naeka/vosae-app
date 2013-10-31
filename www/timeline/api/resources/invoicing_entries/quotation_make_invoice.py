# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from timeline.api.resources.base import TimelineEntryBaseResource
from timeline.api.doc import HELP_TEXT
from timeline.models import invoicing_entries


__all__ = (
    'QuotationMakeInvoiceResource',
    'QuotationMakeDownPaymentInvoiceResource',
)


class QuotationMakeInvoiceResource(TimelineEntryBaseResource):
    quotation_reference = base_fields.CharField(
        attribute='quotation__reference',
        help_text=HELP_TEXT['quotation_make_invoice']['quotation'],
    )
    invoice_reference = base_fields.CharField(
        attribute='invoice__reference',
        help_text=HELP_TEXT['quotation_make_invoice']['invoice'],
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

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'quotation_make_down_payment_invoice'
        object_class = invoicing_entries.QuotationMakeDownPaymentInvoice
