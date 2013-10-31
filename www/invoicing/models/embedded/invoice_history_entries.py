# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now as datetime_now
from mongoengine import EmbeddedDocument, fields

from invoicing import HISTORY_STATES


__all__ = (
    'InvoiceHistoryEntry',
    'ActionHistoryEntry',
    'ChangedStateHistoryEntry',
    'SentHistoryEntry'
)


class InvoiceHistoryEntry(EmbeddedDocument):

    """An history entry associated to an :class:`~invoicing.models.InvoiceBase`."""
    datetime = fields.DateTimeField(required=True, default=datetime_now)
    issuer = fields.ReferenceField("VosaeUser", required=True)
    revision = fields.UUIDField(binary=True)

    meta = {
        "allow_inheritance": True
    }


class ActionHistoryEntry(InvoiceHistoryEntry):

    """Action (create-update-cancel) entry"""
    ACTIONS = ('CREATED', 'UPDATED')
    action = fields.StringField(required=True, choices=ACTIONS)


class ChangedStateHistoryEntry(InvoiceHistoryEntry):

    """Marked as <state> entry"""
    state = fields.StringField(required=True, choices=HISTORY_STATES)


class SentHistoryEntry(InvoiceHistoryEntry):

    """Sent entry"""
    SENT_METHODS = (
        'EMAIL', _('Email'),
    )
    sent_method = fields.StringField(required=True, choices=SENT_METHODS)
    sent_to = fields.StringField(required=True, max_length=128)
