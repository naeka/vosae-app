# -*- coding:Utf-8 -*-

from django.conf import settings
from mongoengine import EmbeddedDocument, fields


__all__ = (
    'VosaeUserSettings',
)


class VosaeUserSettings(EmbeddedDocument):

    """
    Settings related to a :class:`~core.models.VosaeUser`.
    """
    language_code = fields.StringField(choices=settings.LANGUAGES)
    gravatar_email = fields.EmailField()
    email_signature = fields.StringField(max_length=2048)
