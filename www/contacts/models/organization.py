# -*- coding:Utf-8 -*-

from mongoengine import fields

from vosae_utils import SearchDocumentMixin
from pyes import mappings as search_mappings

from contacts.models.entity import Entity


__all__ = (
    'Organization',
)


class Organization(Entity, SearchDocumentMixin):

    """A wrapper to an *organization* entity."""
    TYPE = "ORGANIZATION"
    _contacts = None

    corporate_name = fields.StringField(max_length=64, required=True)
    tags = fields.ListField(fields.StringField(max_length=32))

    meta = {
        "indexes": ["corporate_name"]
    }

    class Meta():
        document_type = 'organization'
        document_boost = 1
        fields = [
            search_mappings.StringField(name="corporate_name", boost=document_boost * 3.0, store=True, term_vector="with_positions_offsets", index="analyzed"),
        ]

    def __unicode__(self):
        return self.corporate_name

    def __getstate__(self):
        # Reset cached queryset for pickle
        self_dict = super(Organization, self).__getstate__()
        self_dict['_contacts'] = None
        return self_dict

    @property
    def contacts(self):
        from contacts.models.contact import Contact
        if self._contacts is None:
            self._contacts = Contact.objects.filter(state='ACTIVE', organization=self)
        return self._contacts

    @contacts.setter
    def contacts(self, value):
        pass

    @contacts.deleter
    def contacts(self, value):
        pass

    def get_search_kwargs(self):
        return {
            'corporate_name': self.corporate_name
        }
