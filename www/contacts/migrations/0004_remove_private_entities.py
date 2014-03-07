# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from contacts.models import Entity


class Migration(DataMigration):

    def forwards(self, orm):
        Entity.objects.update(__raw__={'$unset': {'private': 1}})

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {

    }

    complete_apps = ['contacts']
    symmetrical = True
