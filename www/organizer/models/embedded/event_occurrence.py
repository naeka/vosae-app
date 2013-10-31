# -*- coding:Utf-8 -*-

from mongoengine import EmbeddedDocument, fields


__all__ = (
    'EventOccurrence',
)


class EventOccurrence(EmbeddedDocument):

    """Represent event's occurences"""
    id = fields.StringField(required=True)
    start = fields.DateTimeField(required=True)
    end = fields.DateTimeField(required=True)
