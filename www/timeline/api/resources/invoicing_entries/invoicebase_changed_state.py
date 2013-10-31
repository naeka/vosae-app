# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from timeline.api.resources.base import TimelineEntryBaseResource
from timeline.api.doc import HELP_TEXT
from timeline.models import invoicing_entries


__all__ = (
    'QuotationChangedStateResource',
    'InvoiceChangedStateResource',
    'DownPaymentInvoiceChangedStateResource',
    'CreditNoteChangedStateResource',
)


class InvoiceBaseChangedStateResource(TimelineEntryBaseResource):
    previous_state = base_fields.CharField(
        attribute='previous_state',
        help_text=HELP_TEXT['invoicebase_changed_state']['previous_state'],
    )
    new_state = base_fields.CharField(
        attribute='new_state',
        help_text=HELP_TEXT['invoicebase_changed_state']['new_state'],
    )

    class Meta(TimelineEntryBaseResource.Meta):
        pass


class QuotationChangedStateResource(InvoiceBaseChangedStateResource):
    quotation_reference = base_fields.CharField(
        attribute='quotation__reference',
        help_text=HELP_TEXT['invoicebase_saved']['quotation'],
    )

    quotation = fields.ReferenceField(
        to='invoicing.api.resources.QuotationResource',
        attribute='quotation',
        help_text=HELP_TEXT['invoicebase_changed_state']['quotation']
    )

    class Meta(InvoiceBaseChangedStateResource.Meta):
        resource_name = 'quotation_changed_state'
        object_class = invoicing_entries.QuotationChangedState


class InvoiceChangedStateResource(InvoiceBaseChangedStateResource):
    invoice_reference = base_fields.CharField(
        attribute='invoice__reference',
        help_text=HELP_TEXT['invoicebase_saved']['invoice'],
    )

    invoice = fields.ReferenceField(
        to='invoicing.api.resources.InvoiceResource',
        attribute='invoice',
        help_text=HELP_TEXT['invoicebase_changed_state']['invoice']
    )

    class Meta(InvoiceBaseChangedStateResource.Meta):
        resource_name = 'invoice_changed_state'
        object_class = invoicing_entries.InvoiceChangedState


class DownPaymentInvoiceChangedStateResource(InvoiceBaseChangedStateResource):
    down_payment_invoice_reference = base_fields.CharField(
        attribute='down_payment_invoice__reference',
        help_text=HELP_TEXT['invoicebase_saved']['down_payment_invoice'],
    )

    down_payment_invoice = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='down_payment_invoice',
        help_text=HELP_TEXT['invoicebase_changed_state']['down_payment_invoice']
    )

    class Meta(InvoiceBaseChangedStateResource.Meta):
        resource_name = 'down_payment_invoice_changed_state'
        object_class = invoicing_entries.DownPaymentInvoiceChangedState


class CreditNoteChangedStateResource(InvoiceBaseChangedStateResource):
    credit_note_reference = base_fields.CharField(
        attribute='credit_note__reference',
        help_text=HELP_TEXT['invoicebase_saved']['credit_note'],
    )

    credit_note = fields.ReferenceField(
        to='invoicing.api.resources.CreditNoteResource',
        attribute='credit_note',
        help_text=HELP_TEXT['invoicebase_changed_state']['credit_note']
    )

    class Meta(InvoiceBaseChangedStateResource.Meta):
        resource_name = 'credit_note_changed_state'
        object_class = invoicing_entries.CreditNoteChangedState
