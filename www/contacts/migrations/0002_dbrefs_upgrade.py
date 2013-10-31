# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from contacts.models import Contact, Organization, ContactGroup


class Migration(DataMigration):

    def forwards(self, orm):
        # Contact
        for contact in Contact.objects():
            contact._changed_fields = ['tenant', 'creator', 'photo', 'organization', 'subscribers']
            contact.save()

        # Organization
        for organization in Organization.objects():
            organization._changed_fields = ['tenant', 'creator', 'photo', 'subscribers']
            organization.save()

        # ContactGroup
        for contact_group in ContactGroup.objects():
            contact_group._changed_fields = ['tenant']
            contact_group.save()

    def backwards(self, orm):
        # Same ops, handled on save
        self.forwards(orm)

    models = {

    }

    complete_apps = ['contacts']
    symmetrical = True
