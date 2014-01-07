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
            # entity_saved
            'contact_saved_te': contacts_entries.ContactSavedResource,
            'organization_saved_te': contacts_entries.OrganizationSavedResource,

            # invoicebase_saved
            'quotation_saved_te': invoicing_entries.QuotationSavedResource,
            'purchase_order_saved_te': invoicing_entries.PurchaseOrderSavedResource,
            'invoice_saved_te': invoicing_entries.InvoiceSavedResource,
            'down_payment_invoice_saved_te': invoicing_entries.DownPaymentInvoiceSavedResource,
            'credit_note_saved_te': invoicing_entries.CreditNoteSavedResource,
            
            # invoicebase_changed_state
            'quotation_changed_state_te': invoicing_entries.QuotationChangedStateResource,
            'purchase_order_changed_state_te': invoicing_entries.PurchaseOrderChangedStateResource,
            'invoice_changed_state_te': invoicing_entries.InvoiceChangedStateResource,
            'down_payment_invoice_changed_state_te': invoicing_entries.DownPaymentInvoiceChangedStateResource,
            'credit_note_changed_state_te': invoicing_entries.CreditNoteChangedStateResource,
            
            # make_purchase_order
            'quotation_make_purchase_order_te': invoicing_entries.QuotationMakePurchaseOrderResource,

            # make_invoice
            'quotation_make_invoice_te': invoicing_entries.QuotationMakeInvoiceResource,
            'quotation_make_down_payment_invoice_te': invoicing_entries.QuotationMakeDownPaymentInvoiceResource,
            'purchase_order_make_invoice_te': invoicing_entries.PurchaseOrderMakeInvoiceResource,
            'purchase_order_make_down_payment_invoice_te': invoicing_entries.PurchaseOrderMakeDownPaymentInvoiceResource,
            
            # invoice_cancelled
            'invoice_cancelled_te': invoicing_entries.InvoiceCancelledResource,
            'down_payment_invoice_cancelled_te': invoicing_entries.DownPaymentInvoiceCancelledResource,
        }
