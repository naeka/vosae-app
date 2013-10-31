# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import VosaeResource
from organizer.models.embedded.reminder import ReminderSettings, ReminderEntry
from organizer.api.doc import HELP_TEXT


__all__ = (
    'ReminderEntryResource',
    'ReminderSettingsResource',
)


class ReminderEntryResource(VosaeResource):
    method = base_fields.CharField(
        attribute='method',
        help_text=HELP_TEXT['reminder']['method']
    )
    minutes = base_fields.IntegerField(
        attribute='minutes',
        help_text=HELP_TEXT['reminder']['minutes']
    )

    class Meta(VosaeResource.Meta):
        object_class = ReminderEntry


class ReminderSettingsResource(VosaeResource):
    use_default = base_fields.BooleanField(
        attribute='use_default',
        help_text=HELP_TEXT['reminder']['use_default']
    )

    overrides = fields.EmbeddedListField(
        of='organizer.api.resources.ReminderEntryResource',
        attribute='overrides',
        null=True,
        blank=True,
        full=True,
        help_text=HELP_TEXT['reminder']['overrides']
    )

    class Meta(VosaeResource.Meta):
        object_class = ReminderSettings
