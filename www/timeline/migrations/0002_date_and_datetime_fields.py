# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from timeline.models import TimelineEntry


class Migration(DataMigration):

    def forwards(self, orm):
        # Notification
        TimelineEntry.objects.all().update(__raw__={"$rename": {"date": "datetime"}})

    def backwards(self, orm):
        # Notification
        TimelineEntry.objects.all().update(__raw__={"$rename": {"datetime": "date"}})

    models = {

    }

    complete_apps = ['timeline']
    symmetrical = True
