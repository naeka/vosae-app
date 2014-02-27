# -*- coding:Utf-8 -*-

from HTMLParser import HTMLParser


__all__ = (
    'TagsStripper',
)


SELF_CLOSING_TAGS = ['br', 'hr']


class TagsStripper(HTMLParser):
    def __init__(self, allowed_tags=[]):
        self.allowed_tags = allowed_tags
        self.reset()
        self.fed = []

    def handle_starttag(self, tag, attrs):
        if tag in self.allowed_tags:
            self.fed.append(u'<{0}>'.format(tag))

    def handle_endtag(self, tag):
        if tag in self.allowed_tags and tag not in SELF_CLOSING_TAGS:
            self.fed.append(u'</{0}>'.format(tag))

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return u''.join(self.fed)
