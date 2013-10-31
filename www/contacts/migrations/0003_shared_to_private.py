# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from contacts.models import Entity


class Migration(DataMigration):

    def forwards(self, orm):
        for entity in Entity.objects():
            if 'shared' in entity._data:
                entity._changed_fields.append('shared')
            if entity._data.get('shared', None) is True:
                entity.private = False
            entity.save()

    def backwards(self, orm):
        for entity in Entity.objects():
            if 'private' in entity._data:
                entity._changed_fields.append('private')
            if entity._data.get('private', None) is False:
                entity.shared = True
            entity.save()

    models = {

    }

    complete_apps = ['contacts']
    symmetrical = True
