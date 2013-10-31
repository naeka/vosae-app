# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from notification.api.resources.base import NotificationBaseResource
from notification.api.doc import HELP_TEXT
from notification.models import contacts_notifications


__all__ = (
    'ContactSavedResource',
    'OrganizationSavedResource',
)


class ContactSavedResource(NotificationBaseResource):
    contact_name = base_fields.CharField(
        attribute='contact__get_full_name',
        help_text=HELP_TEXT['entity_saved']['contact'],
    )

    contact = fields.ReferenceField(
        to='contacts.api.resources.ContactResource',
        attribute='contact',
        help_text=HELP_TEXT['entity_saved']['contact']
    )

    class Meta(NotificationBaseResource.Meta):
        resource_name = 'contact_saved'
        object_class = contacts_notifications.ContactSaved


class OrganizationSavedResource(NotificationBaseResource):
    organization_name = base_fields.CharField(
        attribute='organization__corporate_name',
        help_text=HELP_TEXT['entity_saved']['organization'],
    )

    organization = fields.ReferenceField(
        to='contacts.api.resources.OrganizationResource',
        attribute='organization',
        help_text=HELP_TEXT['entity_saved']['organization']
    )

    class Meta(NotificationBaseResource.Meta):
        resource_name = 'organization_saved'
        object_class = contacts_notifications.OrganizationSaved
