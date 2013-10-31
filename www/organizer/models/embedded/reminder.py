# -*- coding:Utf-8 -*-

from mongoengine import EmbeddedDocument, fields


__all__ = (
    'ReminderEntry',
    'ReminderSettings',
)


class ReminderEntry(EmbeddedDocument):

    """
    Per-event reminders settings
    """
    METHODS = (
        'EMAIL',
        'POPUP'
    )

    method = fields.StringField(choices=METHODS, required=True)
    minutes = fields.IntField(min_value=0, max_value=21600, required=True)  # Max 15 days before


class ReminderSettings(EmbeddedDocument):

    """
    Per-event reminders settings
    """
    use_default = fields.BooleanField(default=True)
    overrides = fields.ListField(fields.EmbeddedDocumentField("ReminderEntry"))


class NextReminder(EmbeddedDocument):
    at = fields.DateTimeField(required=True)
    threshold = fields.IntField(min_value=0, max_value=21600, required=True)
