# -*- coding:Utf-8 -*-

from mongoengine import Document, fields

from organizer.models.embedded import ReminderEntry


__all__ = (
    'CalendarList',
)


class CalendarList(Document):
    """Represent a calendar entry, linked to a :class:`~core.models.VosaeUser`."""
    tenant = fields.ReferenceField("Tenant", required=True)
    vosae_user = fields.ReferenceField("VosaeUser", required=True)
    calendar = fields.ReferenceField("VosaeCalendar", required=True)
    summary_override = fields.StringField(max_length=64)
    color = fields.StringField(regex=r'#[0-9a-fA-F]{6}$', required=True, default='#44b2ae')
    selected = fields.BooleanField(required=True, default=False)
    reminders = fields.ListField(fields.EmbeddedDocumentField("ReminderEntry"), default=lambda: [ReminderEntry(method='POPUP', minutes=10)])

    meta = {
        "indexes": ["tenant", "vosae_user"],

        # Vosae specific
        "vosae_mandatory_permissions": ("organizer_access",),
    }
