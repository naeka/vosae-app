# -*- coding:Utf-8 -*-

from django.conf import settings
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    PageBreak,
    Paragraph as _Paragraph
)

__all__ = (
    'register_fonts_from_paths',
    'Paragraph',
    'RestartPageBreak',
    'ReportingDocTemplate',
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


def sanitize(text):
    """
    Replace interpreted chars.
    """
    REPLACE_MAP = [
        (u'&', '&#38;'),
        (u'<', '&#60;'),
        (u'>', '&#62;'),
        (u'\n', '<br />'),
        (u'\r', ''),
    ]
    for p, q in REPLACE_MAP:
        text = text.replace(p, q)
    return text


def normalize(text):
    """
    Ensure that text is unicode.
    """
    if not isinstance(text, unicode):
        text = unicode(text)
    return text


def Paragraph(txt, *args, **kwargs):
    if not txt:
        return _Paragraph(u'', *args, **kwargs)
    return _Paragraph(sanitize(normalize(txt)), *args, **kwargs)


class RestartPageBreak(PageBreak):

    """
    Insert a page break and restart the page numbering.
    """
    pass


class ReportingDocTemplate(BaseDocTemplate):

    def __init__(self, *args, **kwargs):
        BaseDocTemplate.__init__(self, *args, **kwargs)
        self.numPages = 0
        self._lastNumPages = 0
        self.setProgressCallBack(self._onProgress_cb)

        # For batch reports with several PDFs concatenated
        self.restartDoc = False
        self.restartDocIndex = 0
        self.restartDocPageNumbers = []

    def handle_documentBegin(self):
        BaseDocTemplate.handle_documentBegin(self)
        self.canv._doc.info.producer = 'Vosae - %s' % settings.VOSAE_WWW_DOMAIN

    def afterFlowable(self, flowable):
        self.numPages = max(self.canv.getPageNumber(), self.numPages)
        if isinstance(flowable, RestartPageBreak):
            self.restartDoc = True
            self.restartDocIndex += 1
            self.restartDocPageNumbers.append(self.page)

    # here the real hackery starts ... thanks Ralph
    def _allSatisfied(self):
        """ Called by multi-build - are all cross-references resolved? """
        if self._lastnumPages < self.numPages:
            return 0
        return BaseDocTemplate._allSatisfied(self)

    def _onProgress_cb(self, what, arg):
        if what == 'STARTED':
            self._lastnumPages = self.numPages
            self.restartDocIndex = 0
            #self.restartDocPageNumbers = []

    def page_index(self):
        """
        Return the current page index as a tuple (current_page, total_pages)

        This is the ugliest thing I've done in the last two years.
        For this I'll burn in programmer hell.

        At least it is contained here.

        (Determining the total number of pages in reportlab is a mess anyway...)
        """

        current_page = self.page
        total_pages = self.numPages

        if self.restartDoc:
            if self.restartDocIndex:
                current_page = current_page - self.restartDocPageNumbers[self.restartDocIndex - 1] + 1
                if len(self.restartDocPageNumbers) > self.restartDocIndex:
                    total_pages = self.restartDocPageNumbers[self.restartDocIndex] - self.restartDocPageNumbers[self.restartDocIndex - 1] + 1
            else:
                total_pages = self.restartDocPageNumbers[0]

        # Ensure total pages is always at least 1
        total_pages = max(1, total_pages)

        return {
            'current': current_page,
            'total': total_pages
        }
