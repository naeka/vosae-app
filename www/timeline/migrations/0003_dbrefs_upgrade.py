# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from timeline.models import (
    ContactSaved,
    OrganizationSaved,
    InvoiceCancelled,
    DownPaymentInvoiceCancelled,
    QuotationChangedState,
    InvoiceChangedState,
    DownPaymentInvoiceChangedState,
    CreditNoteChangedState,
    QuotationSaved,
    InvoiceSaved,
    DownPaymentInvoiceSaved,
    CreditNoteSaved,
    QuotationMakeInvoice,
    QuotationMakeDownPaymentInvoice
)


class Migration(DataMigration):

    def forwards(self, orm):
        # ContactSaved
        for notification in ContactSaved.objects():
            notification._changed_fields = ['tenant', 'issuer', 'contact']
            notification.save()

        # OrganizationSaved
        for notification in OrganizationSaved.objects():
            notification._changed_fields = ['tenant', 'issuer', 'organization']
            notification.save()

        # InvoiceCancelled
        for notification in InvoiceCancelled.objects():
            notification._changed_fields = ['tenant', 'issuer', 'invoice', 'credit_note']
            notification.save()

        # DownPaymentInvoiceCancelled
        for notification in DownPaymentInvoiceCancelled.objects():
            notification._changed_fields = ['tenant', 'issuer', 'down_payment_invoice', 'credit_note']
            notification.save()

        # QuotationChangedState
        for notification in QuotationChangedState.objects():
            notification._changed_fields = ['tenant', 'issuer', 'quotation']
            notification.save()

        # InvoiceChangedState
        for notification in InvoiceChangedState.objects():
            notification._changed_fields = ['tenant', 'issuer', 'invoice']
            notification.save()

        # DownPaymentInvoiceChangedState
        for notification in DownPaymentInvoiceChangedState.objects():
            notification._changed_fields = ['tenant', 'issuer', 'down_payment_invoice']
            notification.save()

        # CreditNoteChangedState
        for notification in CreditNoteChangedState.objects():
            notification._changed_fields = ['tenant', 'issuer', 'credit_note']
            notification.save()

        # QuotationSaved
        for notification in QuotationSaved.objects():
            notification._changed_fields = ['tenant', 'issuer', 'quotation']
            notification.save()

        # InvoiceSaved
        for notification in InvoiceSaved.objects():
            notification._changed_fields = ['tenant', 'issuer', 'invoice']
            notification.save()

        # DownPaymentInvoiceSaved
        for notification in DownPaymentInvoiceSaved.objects():
            notification._changed_fields = ['tenant', 'issuer', 'down_payment_invoice']
            notification.save()

        # CreditNoteSaved
        for notification in CreditNoteSaved.objects():
            notification._changed_fields = ['tenant', 'issuer', 'credit_note']
            notification.save()

        # QuotationMakeInvoice
        for notification in QuotationMakeInvoice.objects():
            notification._changed_fields = ['tenant', 'issuer', 'quotation', 'invoice']
            notification.save()

        # QuotationMakeDownPaymentInvoice
        for notification in QuotationMakeDownPaymentInvoice.objects():
            notification._changed_fields = ['tenant', 'issuer', 'quotation', 'down_payment_invoice']
            notification.save()

    def backwards(self, orm):
        # Same ops, handled on save
        self.forwards(orm)

    models = {

    }

    complete_apps = ['timeline']
    symmetrical = True
