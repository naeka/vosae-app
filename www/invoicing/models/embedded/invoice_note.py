# -*- coding:Utf-8 -*-

from mongoengine import EmbeddedDocument, fields
from django.utils.timezone import now


__all__ = ('InvoiceNote',)


class InvoiceNote(EmbeddedDocument):

    """A note associated to an :class:`~invoicing.models.InvoiceBase`."""
    datetime = fields.DateTimeField(required=True, default=now)
    issuer = fields.ReferenceField("VosaeUser", required=True)
    note = fields.StringField(required=True, max_length=1024)
