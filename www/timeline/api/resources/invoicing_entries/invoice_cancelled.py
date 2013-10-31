# -*- coding:Utf-8 -*-

from tastypie_mongoengine import fields

from timeline.api.resources.base import TimelineEntryBaseResource
from timeline.api.doc import HELP_TEXT
from timeline.models import invoicing_entries


__all__ = (
    'InvoiceCancelledResource',
    'DownPaymentInvoiceCancelledResource',
)


class InvoiceCancelledResource(TimelineEntryBaseResource):
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

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'invoice_cancelled'
        object_class = invoicing_entries.InvoiceCancelled


class DownPaymentInvoiceCancelledResource(TimelineEntryBaseResource):
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

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'down_payment_invoice_cancelled'
        object_class = invoicing_entries.DownPaymentInvoiceCancelled
