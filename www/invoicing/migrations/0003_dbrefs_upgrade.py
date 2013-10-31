# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from invoicing.models import (
    CreditNote,
    DownPaymentInvoice,
    Invoice,
    Item,
    Payment,
    Quotation,
    Tax
)


def set_embedded_changed_fields(invoice_base):
    def update_revision(revision):
        revision._changed_fields = ['issuer', 'contact', 'organization', 'pdf']
        for idx, line_item in enumerate(revision.line_items):
            revision.line_items[idx]._changed_fields = ['tax']
    update_revision(invoice_base.current_revision)
    for idx, revision in enumerate(invoice_base.revisions):
        update_revision(invoice_base.revisions[idx])
    for idx, history_entry in enumerate(invoice_base.history):
        invoice_base.history[idx]._changed_fields = ['issuer']
    for idx, note in enumerate(invoice_base.notes):
        invoice_base.notes[idx]._changed_fields = ['issuer']


class Migration(DataMigration):

    def forwards(self, orm):
        # Quotation
        for quotation in Quotation.objects():
            quotation._changed_fields = ['tenant', 'issuer', 'organization', 'contact', 'attachments', 'related_invoice', 'down_payments', 'subscribers']
            set_embedded_changed_fields(quotation)
            quotation.save()

        # Invoice
        for invoice in Invoice.objects():
            invoice._changed_fields = ['tenant', 'issuer', 'organization', 'contact', 'attachments', 'related_quotation', 'payments', 'subscribers']
            set_embedded_changed_fields(invoice)
            invoice.save()

        # DownPaymentInvoice
        for down_payment_invoice in DownPaymentInvoice.objects():
            down_payment_invoice._changed_fields = ['tenant', 'issuer', 'organization', 'contact', 'attachments', 'related_quotation', 'payments', 'tax_applied', 'subscribers']
            set_embedded_changed_fields(down_payment_invoice)
            down_payment_invoice.save()

        # CreditNote
        for credit_note in CreditNote.objects():
            credit_note._changed_fields = ['tenant', 'issuer', 'organization', 'contact', 'attachments', 'related_invoice', 'subscribers']
            set_embedded_changed_fields(credit_note)
            credit_note.save()

        # Item
        for item in Item.objects():
            item._changed_fields = ['tenant', 'currency', 'tax']
            item.save()

        # Payment
        for payment in Payment.objects():
            payment._changed_fields = ['tenant', 'issuer', 'currency']
            payment.save()

        # Tax
        for tax in Tax.objects():
            tax._changed_fields = ['tenant']
            tax.save()

    def backwards(self, orm):
        # Same ops, handled on save
        self.forwards(orm)

    models = {

    }

    complete_apps = ['invoicing']
    symmetrical = True
