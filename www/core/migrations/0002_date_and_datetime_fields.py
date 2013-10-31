# -*- coding: utf-8 -*-

from south.v2 import SchemaMigration
from core.models import VosaeGroup


class Migration(SchemaMigration):

    def forwards(self, orm):
        VosaeGroup.objects.all().update(__raw__={"$rename": {"created_date": "created_at"}})  # Old
        VosaeGroup.objects.all().update(__raw__={"$rename": {"creation_datetime": "created_at"}})

    def backwards(self, orm):
        VosaeGroup.objects.all().update(__raw__={"$rename": {"created_at": "creation_datetime"}})

    models = {

    }

    complete_apps = ['core']
