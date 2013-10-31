# -*- coding:Utf-8 -*-

from mongoengine import fields

from notification.models.organizer_notifications.organizer_notification import OrganizerNotification


__all__ = (
    'EventReminder',
)


class EventReminder(OrganizerNotification):
    vosae_event = fields.ReferenceField("VosaeEvent", required=True)
    occurs_at = fields.DateTimeField(required=True)
    summary = fields.StringField(required=True)
