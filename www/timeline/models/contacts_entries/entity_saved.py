# -*- coding:Utf-8 -*-

from mongoengine import fields

from timeline.models.contacts_entries.contacts_timeline_entry import ContactsTimelineEntry
from core.fields import NotPrivateReferenceField


__all__ = (
    'ContactSaved',
    'OrganizationSaved',
)


class ContactSaved(ContactsTimelineEntry):
    contact = NotPrivateReferenceField("Contact", required=True)
    created = fields.BooleanField(required=True)


class OrganizationSaved(ContactsTimelineEntry):
    organization = NotPrivateReferenceField("Organization", required=True)
    created = fields.BooleanField(required=True)
