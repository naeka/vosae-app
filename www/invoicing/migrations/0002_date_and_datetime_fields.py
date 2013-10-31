# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from invoicing.models import Payment, InvoiceBase


class Migration(DataMigration):

    def forwards(self, orm):
        # Payments
        Payment.objects.all().update(__raw__={"$rename": {"issue_date": "issued_at"}})

        # InvoiceNote
        for invoice_base in InvoiceBase.objects.all():
            if invoice_base.notes:
                for note in invoice_base.notes:
                    if note.registration_date:
                        note.datetime = note.registration_date
                        note.registration_date = None
                        if not 'datetime' in note._changed_fields:
                            note._changed_fields.append('datetime')
                        if not 'registration_date' in note._changed_fields:
                            note._changed_fields.append('registration_date')
                invoice_base.save()

    def backwards(self, orm):
        # Payments
        Payment.objects.all().update(__raw__={"$rename": {"issued_at": "issue_date"}})

        # InvoiceNote
        for invoice_base in InvoiceBase.objects.all():
            if invoice_base.notes:
                for note in invoice_base.notes:
                    if note.registration_date:
                        note.registration_date = note.datetime
                        note.datetime = None
                        if not 'datetime' in note._changed_fields:
                            note._changed_fields.append('datetime')
                        if not 'registration_date' in note._changed_fields:
                            note._changed_fields.append('registration_date')
                invoice_base.save()

    models = {

    }

    complete_apps = ['invoicing']
    symmetrical = True
