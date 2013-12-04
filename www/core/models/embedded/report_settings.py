# -*- coding:Utf-8 -*-

from django.conf import settings
from mongoengine import EmbeddedDocument, fields

from core.pdf.conf.fonts import mapping


__all__ = (
    'ReportSettings',
)


class ReportSettings(EmbeddedDocument):

    """ReportSettings stores various informations used to customize reports"""
    font_name = fields.StringField(required=True, default='bariol', choices=mapping.keys())
    font_size = fields.IntField(required=True, default=10)
    base_color = fields.StringField()
    force_bw = fields.BooleanField(required=True, default=False)
    language = fields.StringField(choices=settings.LANGUAGES, required=True, default='en')
