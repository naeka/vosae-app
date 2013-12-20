# -*- coding:Utf-8 -*-

from django.conf import settings

from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os


__all__ = (
    'register_fonts_from_paths',
    'mapping',
    'get_font',

    # Fonts themselves
    'times',
    'courier',
    'helvetica',
    'bariol',
)


def register_fonts_from_paths(regular, italic=None, bold=None, bolditalic=None, font_name='Reporting'):
    """
    Pass paths to TTF files which should be used for the PDFDocument
    """
    pdfmetrics.registerFont(TTFont('%s' % font_name, regular))
    pdfmetrics.registerFont(TTFont('%s-Italic' % font_name, italic or regular))
    pdfmetrics.registerFont(TTFont('%s-Bold' % font_name, bold or regular))
    pdfmetrics.registerFont(TTFont('%s-BoldItalic' % font_name, bolditalic or bold or regular))

    addMapping('%s' % font_name, 0, 0, '%s' % font_name)  # regular
    addMapping('%s' % font_name, 0, 1, '%s-Italic' % font_name)  # italic
    addMapping('%s' % font_name, 1, 0, '%s-Bold' % font_name)  # bold
    addMapping('%s' % font_name, 1, 1, '%s-BoldItalic' % font_name)  # bold & italic


class BaseFont(object):
    regular = None
    bold = None
    italic = None
    bold_italic = None

    def __new__(cls, *args, **kwargs):
        new_class = super(BaseFont, cls).__new__(cls, *args, **kwargs)
        if not new_class.regular:
            raise AttributeError('The regular name must be provided')
        new_class.bold = new_class.bold or '{0}-Bold'.format(new_class.regular)
        new_class.italic = new_class.italic or '{0}-Italic'.format(new_class.regular)
        new_class.bold_italic = new_class.bold_italic or '{0}-BoldItalic'.format(new_class.regular)
        return new_class


# Custom fonts registration
register_fonts_from_paths(
    font_name='Bariol',
    regular=os.path.join(settings.FONTS_DIR, 'bariol_regular-webfont.ttf'),
    italic=os.path.join(settings.FONTS_DIR, 'bariol_regular_italic.ttf'),
    bold=os.path.join(settings.FONTS_DIR, 'bariol_bold-webfont.ttf'),
    bolditalic=os.path.join(settings.FONTS_DIR, 'bariol_bold_italic.ttf'),
)


# Fonts
times = type('Times', (BaseFont,), dict(regular='Times-Roman', bold='Times-Bold', italic='Times-Italic', bold_italic='Times-BoldItalic'))()
courier = type('Courier', (BaseFont,), dict(regular='Courier', italic='Courier-Oblique', bold_italic='Courier-BoldOblique'))()
helvetica = type('Helvetica', (BaseFont,), dict(regular='Helvetica', italic='Helvetica-Oblique', bold_italic='Helvetica-BoldOblique'))()
bariol = type('Bariol', (BaseFont,), dict(regular='Bariol'))()

mapping = {
    'times': times,
    'courier': courier,
    'helvetica': helvetica,
    'bariol': bariol
}


def get_font(name):
    return mapping[name]