# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from core.models import Tenant, VosaeFile
from vosae_settings.models import TenantSettings


class Migration(DataMigration):

    def forwards(self, orm):
        for tenant in Tenant.objects():
            used_space = int(VosaeFile.objects.filter(tenant=tenant).sum('size'))
            tenant.tenant_settings.core.quotas.used_space = used_space
            tenant.tenant_settings.save()

    def backwards(self, orm):
        for tenant_settings in TenantSettings.objects():
            tenant_settings.core.quotas = None
            tenant_settings.core._changed_fields += ['quotas']
            tenant_settings.save()

    models = {

    }

    complete_apps = ['vosae_settings']
    symmetrical = True
