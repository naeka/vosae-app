# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from vosae_settings.models import TenantSettings
from invoicing import PAYMENT_CONDITIONS


class Migration(DataMigration):

    def forwards(self, orm):
        for tenant_settings in TenantSettings.objects.all():
            if hasattr(tenant_settings.invoicing, 'due_date_period') or hasattr(tenant_settings.invoicing, 'due_date_end_of_month'):
                tenant_settings.invoicing.payment_conditions = unicode(getattr(tenant_settings.invoicing, 'due_date_period', u'CASH')) + u'D'
                if getattr(tenant_settings.invoicing, 'due_date_end_of_month', None):
                    tenant_settings.invoicing.payment_conditions += u'-EOM'
                if not tenant_settings.invoicing.payment_conditions in PAYMENT_CONDITIONS:
                    tenant_settings.invoicing.payment_conditions = u'CASH'
                tenant_settings.invoicing.due_date_period = None
                tenant_settings.invoicing.due_date_end_of_month = None
                tenant_settings.invoicing._changed_fields += ['due_date_period', 'due_date_end_of_month']
                tenant_settings.save()

    def backwards(self, orm):
        for tenant_settings in TenantSettings.objects.all():
            tenant_settings.invoicing.due_date_period = 0
            tenant_settings.invoicing.due_date_end_of_month = False
            if tenant_settings.invoicing.payment_conditions.startswith('30D'):
                tenant_settings.invoicing.due_date_period = 30
                if tenant_settings.invoicing.payment_conditions.startswith('30D-EOM'):
                    tenant_settings.invoicing.due_date_end_of_month = True
            elif tenant_settings.invoicing.payment_conditions.startswith('45D'):
                tenant_settings.invoicing.due_date_period = 45
                if tenant_settings.invoicing.payment_conditions.startswith('45D-EOM'):
                    tenant_settings.invoicing.due_date_end_of_month = True
            elif tenant_settings.invoicing.payment_conditions.startswith('60D'):
                tenant_settings.invoicing.due_date_period = 60
                if tenant_settings.invoicing.payment_conditions.startswith('60D-EOM'):
                    tenant_settings.invoicing.due_date_end_of_month = True
            tenant_settings.invoicing.payment_conditions = None
            tenant_settings.invoicing._changed_fields += ['payment_conditions']
            tenant_settings.save()

    models = {

    }

    complete_apps = ['vosae_settings']
    symmetrical = True
