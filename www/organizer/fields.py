# -*- coding:Utf-8 -*-

from mongoengine.fields import DateTimeField, StringField
import datetime
import pytz


__all__ = (
    'DateField',
    'TimeZoneField'
)


class tzstr(str):

    def get_tz(self):
        try:
            return pytz.timezone(self)
        except:
            return None


class tzunicode(unicode):

    def get_tz(self):
        try:
            return pytz.timezone(self)
        except:
            return None


class TimeZoneField(StringField):

    """A timezone field."""

    def __get__(self, instance, owner):
        value = super(TimeZoneField, self).__get__(instance, owner)
        if isinstance(value, unicode):
            return tzunicode(value)
        elif isinstance(value, str):
            return tzstr(value)
        return value
