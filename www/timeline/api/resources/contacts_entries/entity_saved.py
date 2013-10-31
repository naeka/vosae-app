# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from timeline.api.resources.base import TimelineEntryBaseResource
from timeline.api.doc import HELP_TEXT
from timeline.models import contacts_entries


__all__ = (
    'ContactSavedResource',
    'OrganizationSavedResource',
)


class ContactSavedResource(TimelineEntryBaseResource):
    contact_name = base_fields.CharField(
        attribute='contact__get_full_name',
        help_text=HELP_TEXT['entity_saved']['contact'],
    )

    contact = fields.ReferenceField(
        to='contacts.api.resources.ContactResource',
        attribute='contact',
        help_text=HELP_TEXT['entity_saved']['contact']
    )

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'contact_saved'
        object_class = contacts_entries.ContactSaved


class OrganizationSavedResource(TimelineEntryBaseResource):
    organization_name = base_fields.CharField(
        attribute='organization__corporate_name',
        help_text=HELP_TEXT['entity_saved']['organization'],
    )

    organization = fields.ReferenceField(
        to='contacts.api.resources.OrganizationResource',
        attribute='organization',
        help_text=HELP_TEXT['entity_saved']['organization']
    )

    class Meta(TimelineEntryBaseResource.Meta):
        resource_name = 'organization_saved'
        object_class = contacts_entries.OrganizationSaved
