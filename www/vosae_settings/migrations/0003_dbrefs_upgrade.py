# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from vosae_settings.models import TenantSettings


class Migration(DataMigration):

    def forwards(self, orm):
        # TenantSettings
        for tenant_settings in TenantSettings.objects():
            tenant_settings._changed_fields = ['tenant']
            tenant_settings.invoicing._changed_fields = ['supported_currencies', 'default_currency']
            tenant_settings.save()

    def backwards(self, orm):
        # Same ops, handled on save
        self.forwards(orm)

    models = {

    }

    complete_apps = ['vosae_settings']
    symmetrical = True
