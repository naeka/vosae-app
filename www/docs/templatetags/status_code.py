# -*- coding:Utf-8 -*-

from django import template

register = template.Library()


def status_code(value):
    if value == '200':
        return u'200 OK'
    elif value == '201':
        return u'201 Created'
    elif value == '202':
        return u'202 Accepted'
    elif value == '204':
        return u'204 No Content'
    elif value == '301':
        return u'301 Moved Permanently'
    elif value == '302':
        return u'302 Found'
    elif value == '400':
        return u'400 Bad Request'
    elif value == '401':
        return u'401 Unauthorized'
    elif value == '403':
        return u'403 Forbidden'
    elif value == '404':
        return u'404 Not Found'
    elif value == '405':
        return u'405 Method Not Allowed'
    elif value == '429':
        return u'429 Too Many Requests'
    elif value == '500':
        return u'500 Internal Server Error'
    elif value == '501':
        return u'501 Not Implemented'
    else:
        return value

register.filter('status_code', status_code)
