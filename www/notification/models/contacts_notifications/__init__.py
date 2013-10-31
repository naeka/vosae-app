# -*- coding:Utf-8 -*-

from mongoengine import signals
from notification.models.base import Notification
from notification.models.contacts_notifications.contacts_notification import ContactsNotification

from notification.models.contacts_notifications import entity_saved
from notification.models.contacts_notifications.entity_saved import *


__all__ = (
    entity_saved.__all__
)


"""
SIGNALS
"""


signals.post_save.connect(Notification.post_save, sender=ContactSaved)
signals.post_save.connect(Notification.post_save, sender=OrganizationSaved)
