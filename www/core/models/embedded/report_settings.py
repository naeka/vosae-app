# -*- coding:Utf-8 -*-

from django.conf import settings
from mongoengine import EmbeddedDocument, fields
from reportlab.lib.colors import HexColor, color2bw

from core.pdf.conf.fonts import mapping
from core.pdf.conf import colors


__all__ = (
    'ReportSettings',
)


class ReportSettings(EmbeddedDocument):

    """ReportSettings stores various informations used to customize reports"""
    font_name = fields.StringField(required=True, default='bariol', choices=mapping.keys())
    font_size = fields.IntField(required=True, default=10)
    font_color = fields.StringField(regex=r'#[0-9a-fA-F]{6}$', required=True, default='#333333')
    base_color = fields.StringField(regex=r'#[0-9a-fA-F]{6}$', required=True, default='#44b2ae')
    force_bw = fields.BooleanField(required=True, default=False)
    language = fields.StringField(choices=settings.LANGUAGES, required=True, default='en')

    @property
    def hex_font_color(self):
        if self.force_bw:
            return color2bw(HexColor(self.font_color))
        else:
            return HexColor(self.font_color)

    @property
    def hex_base_color(self):
        if self.force_bw:
            return color2bw(HexColor(self.base_color))
        else:
            return HexColor(self.base_color)

    @property
    def hex_font_base_color(self):
        if self.hex_base_color.hsl()[2] < 0.6:
            return colors.white
        else:
            return self.hex_font_color
