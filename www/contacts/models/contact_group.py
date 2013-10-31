# -*- coding:Utf-8 -*-

from mongoengine import Document, fields


__all__ = (
    'ContactGroup',
)


class ContactGroup(Document):

    """
    A class for grouping contacts.

    **Not currently used**
    """
    tenant = fields.ReferenceField("Tenant", required=True)
    name = fields.StringField(max_length=64)

    meta = {
        "indexes": ["tenant", "name"]
    }

    def __unicode__(self):
        return self.name
