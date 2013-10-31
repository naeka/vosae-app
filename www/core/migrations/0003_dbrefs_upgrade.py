# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from core.models import Tenant, VosaeFile, VosaeGroup, VosaeUser


class Migration(DataMigration):

    def forwards(self, orm):
        # Tenant
        for tenant in Tenant.objects():
            tenant._changed_fields = ['svg_logo', 'img_logo', 'terms', 'tenant_settings']
            tenant.save()

        # VosaeFile - Can't use `save()` because `uploaded_field` is required
        for vosae_file in VosaeFile.objects():
            vosae_file.update(set__tenant=vosae_file.tenant, set__issuer=vosae_file.issuer)

        # VosaeGroup
        for vosae_group in VosaeGroup.objects():
            vosae_group._changed_fields = ['tenant', 'created_by']
            vosae_group.save(force=True)

        # VosaeUser
        for vosae_user in VosaeUser.objects():
            vosae_user._changed_fields = ['tenant', 'groups']
            vosae_user.save()

    def backwards(self, orm):
        # Same ops, handled on save
        self.forwards(orm)

    models = {

    }

    complete_apps = ['core']
    symmetrical = True
