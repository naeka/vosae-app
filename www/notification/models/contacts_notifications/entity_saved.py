# -*- coding:Utf-8 -*-

from notification.models.contacts_notifications.contacts_notification import ContactsNotification
from core.fields import NotPrivateReferenceField


__all__ = (
    'ContactSaved',
    'OrganizationSaved',
)


class ContactSaved(ContactsNotification):
    contact = NotPrivateReferenceField("Contact", required=True)


class OrganizationSaved(ContactsNotification):
    organization = NotPrivateReferenceField("Organization", required=True)
