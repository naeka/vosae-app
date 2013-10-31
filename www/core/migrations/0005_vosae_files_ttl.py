# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from core.models import VosaeFile


class Migration(DataMigration):

    def forwards(self, orm):
        # VosaeFile - Can't use `save()` because `uploaded_field` is required
        for vosae_file in VosaeFile.objects():
            vosae_file.update(
                __raw__={
                    '$set': {
                        'created_at': vosae_file.id.generation_time,
                        'modified_at': vosae_file.id.generation_time
                    },
                    '$unset': {
                        'temporary': 1
                    }
                }
            )

    def backwards(self, orm):
        # VosaeFile - Can't use `save()` because `uploaded_field` is required
        for vosae_file in VosaeFile.objects():
            vosae_file.update(
                __raw__={
                    '$unset': {
                        'ttl': 1,
                        'created_at': 1,
                        'modified_at': 1
                    },
                    '$set': {
                        'temporary': True if vosae_file.ttl else False
                    }
                }
            )

    models = {

    }

    complete_apps = ['core']
    symmetrical = True
