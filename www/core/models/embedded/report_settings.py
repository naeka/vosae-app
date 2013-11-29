# -*- coding:Utf-8 -*-

from django.conf import settings
from mongoengine import EmbeddedDocument, fields

from core.pdf.colors import SUPPORTED_FONTS


__all__ = (
    'ReportSettings',
)


class ReportSettings(EmbeddedDocument):

    """ReportSettings stores various informations used to customize reports"""
    font_name = fields.StringField(required=True, default='Bariol', choices=SUPPORTED_FONTS)
    font_size = fields.IntField(required=True, default=10)
    base_color = fields.StringField()
    force_bw = fields.BooleanField(required=True, default=False)
    language = fields.StringField(choices=settings.LANGUAGES, required=True, default='en')
