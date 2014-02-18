# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from core.models import VosaeUser
from contacts.models import Entity
from invoicing.models import Item, Tax


class Migration(DataMigration):

    def forwards(self, orm):
        # VosaeUser and Entities (only schema)
        VosaeUser.objects().update(__raw__={"$rename": {"status": "state"}})
        Entity.objects().update(__raw__={"$rename": {"status": "state"}})

        # Item and Tax (schema + data)
        Item.objects().update(__raw__={"$rename": {"status": "state"}})
        Item.objects(state="INACTIVE").update(set__state="DELETED")
        Tax.objects().update(__raw__={"$rename": {"status": "state"}})
        Tax.objects(state="INACTIVE").update(set__state="DELETED")

    def backwards(self, orm):
        # VosaeUser and Entities (only schema)
        VosaeUser.objects().update(__raw__={"$rename": {"state": "status"}})
        Entity.objects().update(__raw__={"$rename": {"state": "status"}})

        # Item and Tax (schema + data)
        Item.objects().update(__raw__={"$rename": {"state": "status"}})
        Item.objects(status="DELETED").update(set__status="INACTIVE")
        Tax.objects().update(__raw__={"$rename": {"state": "status"}})
        Item.objects(status="DELETED").update(set__status="INACTIVE")

    models = {
        
    }

    complete_apps = ['invoicing']
    symmetrical = True
