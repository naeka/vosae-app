# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from notification.api.resources.base import NotificationBaseResource
from notification.api.doc import HELP_TEXT
from notification.models import organizer_notifications


__all__ = (
    'EventReminderResource',
)


class EventReminderResource(NotificationBaseResource):
    occurs_at = base_fields.DateTimeField(
        attribute='occurs_at',
        help_text=HELP_TEXT['event_reminder']['occurs_at'],
    )
    summary = base_fields.CharField(
        attribute='summary',
        help_text=HELP_TEXT['event_reminder']['summary'],
    )

    vosae_event = fields.ReferenceField(
        to='organizer.api.resources.VosaeEventResource',
        attribute='vosae_event',
        help_text=HELP_TEXT['event_reminder']['vosae_event']
    )

    class Meta(NotificationBaseResource.Meta):
        resource_name = 'event_reminder'
        object_class = organizer_notifications.EventReminder
