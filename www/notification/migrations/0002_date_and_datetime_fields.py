# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from notification.models import Notification


class Migration(DataMigration):

    def forwards(self, orm):
        # Notification
        Notification.objects.all().update(__raw__={"$rename": {"send_date": "sent_at"}})

    def backwards(self, orm):
        # Notification
        Notification.objects.all().update(__raw__={"$rename": {"sent_at": "send_date"}})

    models = {

    }

    complete_apps = ['notification']
    symmetrical = True
