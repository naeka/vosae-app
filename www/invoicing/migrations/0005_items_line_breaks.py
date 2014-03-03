# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from invoicing.models import InvoiceBase, Item


class Migration(DataMigration):

    def forwards(self, orm):
        for item in Item.objects():
            if u'\r' in item.description or u'\n' in item.description:
                item.description = item.description.replace(u'\r', u'')
                item.description = item.description.replace(u'\n', u'<br>')
                item.save(validate=False)

        for invoice_base in InvoiceBase.objects():
            need_update = False
            for line_item in invoice_base.current_revision.line_items:
                if u'\r' in line_item.description or u'\n' in line_item.description:
                    line_item.description = line_item.description.replace(u'\r', u'')
                    line_item.description = line_item.description.replace(u'\n', u'<br>')
                    need_update = True
            for revision in invoice_base.revisions:
                for line_item in revision.line_items:
                    if u'\r' in line_item.description or u'\n' in line_item.description:
                        line_item.description = line_item.description.replace(u'\r', u'')
                        line_item.description = line_item.description.replace(u'\n', u'<br>')
                        need_update = True
            if need_update:
                invoice_base.save(validate=False)

    def backwards(self, orm):
        for item in Item.objects():
            if u'<br>' in item.description:
                item.description = item.description.replace(u'<br>', u'\n')
                item.save()

        for invoice_base in InvoiceBase.objects():
            need_update = False
            for line_item in invoice_base.current_revision.line_items:
                if u'<br>' in line_item.description:
                    line_item.description = line_item.description.replace(u'<br>', u'\n')
                    need_update = True
            for revision in invoice_base.revisions:
                for line_item in revision.line_items:
                    if u'<br>' in line_item.description:
                        line_item.description = line_item.description.replace(u'<br>', u'\n')
                        need_update = True
            if need_update:
                invoice_base.save(validate=False)

    models = {
        
    }

    complete_apps = ['invoicing']
    symmetrical = True
