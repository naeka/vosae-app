# -*- coding:Utf-8 -*-

from timeline.api.resources.base import TimelineEntryBaseResource
from timeline.api.resources import contacts_entries, invoicing_entries
from timeline.models import TimelineEntry


__all__ = (
    'TimelineEntryResource',
)


class TimelineEntryResource(TimelineEntryBaseResource):

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'timeline'
        queryset = TimelineEntry.objects.all()

        polymorphic = {
            'contact_saved_te': contacts_entries.ContactSavedResource,
            'organization_saved_te': contacts_entries.OrganizationSavedResource,

            'quotation_saved_te': invoicing_entries.QuotationSavedResource,
            'invoice_saved_te': invoicing_entries.InvoiceSavedResource,
            'down_payment_invoice_saved_te': invoicing_entries.DownPaymentInvoiceSavedResource,
            'credit_note_saved_te': invoicing_entries.CreditNoteSavedResource,
            'quotation_changed_state_te': invoicing_entries.QuotationChangedStateResource,
            'invoice_changed_state_te': invoicing_entries.InvoiceChangedStateResource,
            'down_payment_invoice_changed_state_te': invoicing_entries.DownPaymentInvoiceChangedStateResource,
            'credit_note_changed_state_te': invoicing_entries.CreditNoteChangedStateResource,
            'quotation_make_invoice_te': invoicing_entries.QuotationMakeInvoiceResource,
            'quotation_make_down_payment_invoice_te': invoicing_entries.QuotationMakeDownPaymentInvoiceResource,
            'invoice_cancelled_te': invoicing_entries.InvoiceCancelledResource,
            'down_payment_invoice_cancelled_te': invoicing_entries.DownPaymentInvoiceCancelledResource,
        }
