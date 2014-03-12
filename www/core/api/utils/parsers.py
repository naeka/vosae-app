# -*- coding:Utf-8 -*-

from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint


__all__ = (
    'BASIC_TAGS',
    'TagsStripper',
)


BASIC_TAGS = ['br', 'b', 'i', 'u']

SELF_CLOSING_TAGS = ['br', 'hr']
BASIC_ENTITIES = ['nbsp', 'amp', 'lt', 'gt']


class TagsStripper(HTMLParser):
    def __init__(self, allowed_tags=[]):
        self.allowed_tags = allowed_tags
        self.reset()

    def reset(self):
        HTMLParser.reset(self)  # Old-style class
        self.fed = []

    def handle_starttag(self, tag, attrs):
        if tag in self.allowed_tags:
            self.fed.append(u'<{0}>'.format(tag))

    def handle_endtag(self, tag):
        if tag in self.allowed_tags and tag not in SELF_CLOSING_TAGS:
            self.fed.append(u'</{0}>'.format(tag))

    def handle_data(self, data):
        self.fed.append(data)

    def handle_entityref(self, name):
        """
        Convert HTML entities to their unicode equivalent.  
        Except for ampersand and chevrons that can be in conflict
        """
        if name in BASIC_ENTITIES:
            self.fed.append(u'&{0};'.format(name))
        else:
            char = unichr(name2codepoint[name])
            self.fed.append(char)

    def get_data(self):
        return u''.join(self.fed)
