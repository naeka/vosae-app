# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from core.models import Tenant
from core.pdf.conf.fonts import mapping


class Migration(DataMigration):

    def forwards(self, orm):
        supported_fonts = mapping.keys()
        for tenant in Tenant.objects():
            if tenant.report_settings.font_name.lower() in supported_fonts:
                font_name = tenant.report_settings.font_name.lower()
            else:
                font_name = 'bariol'
            tenant.update(set__report_settings__font_name=font_name)

    def backwards(self, orm):
        supported_fonts = ('Courier', 'Helvetica', 'Bariol')
        for tenant in Tenant.objects():
            if tenant.report_settings.font_name.capitalize() in supported_fonts:
                font_name = tenant.report_settings.font_name.capitalize()
            else:
                font_name = 'Bariol'
            tenant.update(set__report_settings__font_name=font_name)

    models = {
        
    }

    complete_apps = ['core']
    symmetrical = True
