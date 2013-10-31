# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields

from core.api.utils import VosaeResource
from organizer.models.embedded.event_date_time import EventDateTime
from organizer.api.doc import HELP_TEXT


__all__ = (
    'EventDateTimeResource',
)


class EventDateTimeResource(VosaeResource):
    date = base_fields.DateField(
        attribute='date',
        null=True,
        blank=True,
        help_text=HELP_TEXT['event_date_time']['date']
    )
    datetime = base_fields.DateTimeField(
        attribute='datetime',
        null=True,
        blank=True,
        help_text=HELP_TEXT['event_date_time']['datetime']
    )
    timezone = base_fields.CharField(
        attribute='timezone',
        null=True,
        blank=True,
        help_text=HELP_TEXT['event_date_time']['timezone']
    )

    class Meta(VosaeResource.Meta):
        object_class = EventDateTime
