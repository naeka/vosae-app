# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from invoicing.models import Quotation, DownPaymentInvoice, Invoice, CreditNote


def dereference(oids, target_class):
    """Used because of auto_dereference issues with no-more existing fields"""
    try:
        return target_class.objects.with_id(oids)
    except:
        return [target_class.objects.with_id(oid) for oid in oids]


class Migration(DataMigration):

    def forwards(self, orm):
        from invoicing.models import InvoiceBaseGroup
        # Process quotations
        for quotation in Quotation.objects():
            group = InvoiceBaseGroup(tenant=quotation.tenant, quotation=quotation).save()
            if quotation._data.get('down_payments'):
                group.down_payment_invoices = dereference(quotation._data.get('down_payments'), DownPaymentInvoice)
                for down_payment_invoice in group.down_payment_invoices:
                    down_payment_invoice.update(set__group=group)
            if quotation._data.get('related_invoice'):
                group.invoice = dereference(quotation._data.get('related_invoice'), Invoice)
                group.invoice.update(set__group=group)
            if quotation._data.get('related_invoices_cancelled'):
                group.invoices_cancelled = dereference(quotation._data.get('related_invoices_cancelled'), Invoice)
                for invoice_cancelled in group.invoices_cancelled:
                    invoice_cancelled.update(set__group=group)
            group.save()
            quotation.update(set__group=group)
        
        # Process invoices and down-payment invoices
        for invoice in Invoice.objects():
            if not invoice.group.id:
                # Can only be an invoice: down-payment invoices are linked to quotations, so group is set
                group = InvoiceBaseGroup(tenant=quotation.tenant, invoice=invoice).save()
                invoice.update(set__group=group)
            else:
                group = invoice.group
            if invoice._data.get('related_credit_note'):
                group.credit_notes = [dereference(invoice._data.get('related_credit_note'), CreditNote)]
                for credit_note in group.credit_notes:
                    credit_note.update(set__group=group, set__related_to=invoice)
            group.save()


    def backwards(self, orm):
        from mongoengine import Document, fields
        class InvoiceBaseGroup(Document):
            quotation = fields.ReferenceField("Quotation")
            down_payment_invoices = fields.ListField(fields.ReferenceField("DownPaymentInvoice"))
            invoice = fields.ReferenceField("Invoice")
            invoices_cancelled = fields.ListField(fields.ReferenceField("Invoice"))
            credit_notes = fields.ListField(fields.ReferenceField("CreditNote"))

        for group in InvoiceBaseGroup.objects():
            if group.quotation:
                kwargs = dict()
                if group.invoice:
                    kwargs.update(set__related_invoice=group.invoice)
                if group.invoices_cancelled:
                    kwargs.update(set__related_invoices_cancelled=group.invoices_cancelled)
                if group.down_payment_invoices:
                    kwargs.update(set__down_payments=group.down_payment_invoices)
                if kwargs:
                    group.quotation.update(**kwargs)
            if group.down_payment_invoices or group.invoice:
                kwargs = dict()
                if group.credit_notes:
                    kwargs.update(set__related_credit_note=group.credit_notes[0])
                if kwargs:
                    for down_payment_invoice in group.down_payment_invoices:
                        down_payment_invoice.update(**kwargs)
                    if group.invoice:
                        group.invoice.update(**kwargs)
            if group.credit_notes:
                for credit_note in group.credit_notes:
                    if credit_note._data.get('related_to'):
                        credit_note.update(set__related_invoice=dereference(credit_note._data.get('related_to'), Invoice))
                    else:
                        credit_note.update(set__related_invoice=group.invoice)


    models = {
        
    }

    complete_apps = ['invoicing']
    symmetrical = True
