# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from mongoengine import fields

from vosae_utils import SearchDocumentMixin
from pyes import mappings as search_mappings

from core.fields import DateField
from contacts.models.entity import Entity


__all__ = (
    'Contact',
)


class Contact(Entity, SearchDocumentMixin):

    """A wrapper to a *contact* entity."""
    TYPE = "CONTACT"
    CIVILITIES = (
        ("Mr.", _("Mr.")),
        ("Mrs.", _("Mrs.")),
        ("Miss", _("Miss"))
    )

    name = fields.StringField(max_length=64, required=True)
    firstname = fields.StringField(max_length=64, required=True)
    additional_names = fields.StringField(max_length=128)
    civility = fields.StringField(choices=CIVILITIES)
    birthday = DateField()
    role = fields.StringField(max_length=32)
    organization = fields.ReferenceField("Organization")

    meta = {
        "indexes": ["name", "organization"]
    }

    class Meta():
        document_type = 'contact'
        document_boost = 1
        fields = [
            search_mappings.StringField(name="full_name", boost=document_boost * 3.0, store=True, term_vector="with_positions_offsets", index="analyzed"),
            search_mappings.StringField(name="organization", boost=document_boost * 1.8, store=True, term_vector="with_positions_offsets", index="analyzed"),
        ]

    def __unicode__(self):
        return self.get_full_name()

    def get_search_kwargs(self):
        kwargs = {
            'full_name': self.get_full_name()
        }
        if self.organization:
            kwargs['organization'] = self.organization.corporate_name
        return kwargs

    def get_full_name(self, name_first=False, upper_name=False):
        """
        Returns :class:`~contacts.models.Contact` full name according to this format:

        - Firstname Name, *if either the name and firstname are set*
        - Name, *if only the name is set*
        - Firstname, *if only the firstname is set*
        - None, *if neither the name nor the firstname are set*

        :param name_first: invert name and firstname in the first case.
        """
        if self.name and self.firstname:
            name = self.name.upper() if upper_name else self.name
            if name_first:
                return u'{0} {1}'.format(name, self.firstname)
            return u'{0} {1}'.format(self.firstname, name)
        if self.name:
            return self.name.upper() if upper_name else self.name
        if self.firstname:
            return self.firstname
        return None
