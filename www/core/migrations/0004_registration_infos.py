# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from core.models import Tenant, RegistrationInfo, FRRegistrationInfo


class Migration(DataMigration):

    def forwards(self, orm):
        for tenant in Tenant.objects():
            tenant.registration_info = FRRegistrationInfo(
                share_capital="10000 EUR",
                business_entity=u'SARL',
                vat_number=u'vat_number',
                siret=u'siret',
                rcs_number=u'rcs_number'
            )
            tenant.save(validate=False)  # Disabled validation for VAT checks

    def backwards(self, orm):
        for tenant in Tenant.objects():
            tenant.registration_info = RegistrationInfo(vat_number=u'vat_number')
            tenant.save()

    models = {

    }

    complete_apps = ['core']
    symmetrical = True
