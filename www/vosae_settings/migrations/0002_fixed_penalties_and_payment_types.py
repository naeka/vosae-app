# -*- coding: utf-8 -*-

from south.v2 import DataMigration
import decimal
from vosae_settings.models import TenantSettings


class Migration(DataMigration):

    def forwards(self, orm):
        # Tenant settings
        for tenant_settings in TenantSettings.objects.all():
            if hasattr(tenant_settings.invoicing, 'set_penalties'):
                tenant_settings.invoicing.set_penalties = None
                tenant_settings.invoicing._changed_fields.append('set_penalties')
            if hasattr(tenant_settings.invoicing, 'penalties_rate'):
                if tenant_settings.invoicing.penalties_rate != 0:
                    tenant_settings.invoicing.late_fee_rate = tenant_settings.invoicing.penalties_rate
                tenant_settings.invoicing.penalties_rate = None
                tenant_settings.invoicing._changed_fields.append('penalties_rate')
            if hasattr(tenant_settings.invoicing, 'payment_type'):
                tenant_settings.invoicing.accepted_payment_types.append(tenant_settings.invoicing.payment_type)
                tenant_settings.invoicing.payment_type = None
                tenant_settings.invoicing._changed_fields.append('payment_type')
            tenant_settings.save()

    def backwards(self, orm):
        # Tenant settings
        for tenant_settings in TenantSettings.objects.all():
            tenant_settings.invoicing.set_penalties = False
            tenant_settings.invoicing._changed_fields.append('set_penalties')
            if hasattr(tenant_settings.invoicing, 'late_fee_rate'):
                tenant_settings.invoicing.penalties_rate = tenant_settings.invoicing.late_fee_rate
                tenant_settings.invoicing.late_fee_rate = None
                tenant_settings.invoicing._changed_fields.append('late_fee_rate')
            else:
                tenant_settings.invoicing.penalties_rate = decimal.Decimal("0")
            if hasattr(tenant_settings.invoicing, 'accepted_payment_types'):
                tenant_settings.invoicing.payment_type = tenant_settings.invoicing.accepted_payment_types[0]
                tenant_settings.invoicing.accepted_payment_types = None
                tenant_settings.invoicing._changed_fields.append('accepted_payment_types')
            tenant_settings.save()

    models = {

    }

    complete_apps = ['vosae_settings']
    symmetrical = True
