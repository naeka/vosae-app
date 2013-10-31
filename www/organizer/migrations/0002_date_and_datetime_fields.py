# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from organizer.models import VosaeEvent


class Migration(DataMigration):

    def forwards(self, orm):
        # Notification
        VosaeEvent.objects.all().update(__raw__={"$rename": {"created": "created_at", "updated": "updated_at"}})

    def backwards(self, orm):
        # Notification
        VosaeEvent.objects.all().update(__raw__={"$rename": {"created_at": "created", "updated_at": "updated"}})

    models = {

    }

    complete_apps = ['organizer']
    symmetrical = True
