# -*- coding:Utf-8 -*-

from django.conf import settings
from reportlab.platypus import (
    BaseDocTemplate,
    PageBreak,
    Paragraph as _Paragraph
)
import re


__all__ = (
    'Paragraph',
    'RestartPageBreak',
    'ReportingDocTemplate',
)


def sanitize(text):
    """
    Replace interpreted chars and strip non allowed tags.
    """
    REPLACE_MAP = [
        (u'&', '&#38;'),
        (u'\n', '<br />'),
        (u'\r', ''),
    ]
    ALLOWED_TAGS = ['b', 'i', 'u']

    # Strip not allowed tags
    allowed_tags_re = u'({0})'.format(u'|'.join(ALLOWED_TAGS))
    striptags_re = re.compile(ur'</(?!{0}).*?>|<(?!/)(?!{0}).*?>'.format(allowed_tags_re), re.U)
    text = striptags_re.sub(u'', text)

    # Replace interpreted chars
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
