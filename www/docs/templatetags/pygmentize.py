# -*- coding:Utf-8 -*-

from django import template

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

import json
from lxml import etree


register = template.Library()


def pygmentize(value, serializer=None):
    try:
        lexer = get_lexer_by_name(serializer, stripall=True)
        assert serializer in ('json', 'xml', 'yaml', 'text')
    except (ClassNotFound, AssertionError):
        raise Exception("Invalid serializer")
    if serializer == 'json':
        code = json.dumps(json.loads(value), indent=4)
    elif serializer == 'xml':
        code = etree.tostring(etree.fromstring(value), pretty_print=True)
    elif serializer in ('yaml', 'text'):
        code = value
    formatter = HtmlFormatter(cssclass='source')
    return highlight(code, lexer, formatter)


register.filter('pygmentize', pygmentize)
