# -*- coding:Utf-8 -*-

from mongoengine import EmbeddedDocument, fields, ValidationError
import pytz
import datetime

from core.fields import DateField
from organizer.fields import TimeZoneField


__all__ = (
    'EventDateTime',
)


class EventDateTime(EmbeddedDocument):

    """
    An event start (or end) date stored as UTC.

    If timezone is None, the calendar timezone is used.
    """
    date = DateField()
    datetime = fields.DateTimeField()
    timezone = TimeZoneField(choices=pytz.all_timezones)

    def validate(self, value, **kwargs):
        super(EventDateTime, self).validate(value, **kwargs)
        if self.date and self.datetime:
            raise ValidationError('Only one of "date" and "datetime" must be set. The "date" field is used for all-day events.')
        elif not self.date and not self.datetime:
            raise ValidationError('One of "date" and "datetime" must be set.')

    @classmethod
    def _from_son(cls, son):
        obj = super(EventDateTime, cls)._from_son(son)
        if obj._data['datetime'] and obj._data['timezone']:
            tz = pytz.timezone(obj._data['timezone'])
            obj._data['datetime'] = tz.fromutc(obj._data['datetime'])
        return obj

    def is_date(self):
        return self.date and not self.datetime

    def is_datetime(self):
        return self.datetime and not self.date

    def date_or_dt(self):
        if self.is_date():
            return self.date
        return self.datetime

    def __lt__(self, other):
        cmp_res = self.__cmp__(other)
        return cmp_res < 0

    def __le__(self, other):
        cmp_res = self.__cmp__(other)
        return cmp_res <= 0

    def __eq__(self, other):
        cmp_res = self.__cmp__(other)
        return cmp_res == 0

    def __ne__(self, other):
        cmp_res = self.__cmp__(other)
        return cmp_res != 0

    def __gt__(self, other):
        cmp_res = self.__cmp__(other)
        return cmp_res > 0

    def __ge__(self, other):
        cmp_res = self.__cmp__(other)
        return cmp_res >= 0

    def __cmp__(self, other):
        if isinstance(other, datetime.datetime):
            if self.is_datetime():
                return cmp(self.datetime, other)
            else:
                return cmp(self.date, other.date())
        elif isinstance(other, datetime.date):
            if self.is_datetime():
                return cmp(self.datetime.date(), other)
            else:
                return cmp(self.date, other)
        elif isinstance(other, EventDateTime):
            if self.is_datetime() and other.is_datetime():
                return cmp(self.datetime, other.datetime)
            elif self.is_datetime() and not other.is_datetime():
                if isinstance(other.date, datetime.date):
                    return cmp(self.datetime, datetime.datetime.combine(other.date, datetime.time()))
                else:
                    return 1
            elif not self.is_datetime() and other.is_datetime():
                if isinstance(self.date, datetime.date):
                    return cmp(datetime.datetime.combine(self.date, datetime.time()), other.datetime)
                else:
                    if not isinstance(self.date, datetime.date) and not isinstance(other.date, datetime.date):
                        return 0
                    elif isinstance(self.date, datetime.date) and not isinstance(other.date, datetime.date):
                        return 1
                    elif not isinstance(self.date, datetime.date) and isinstance(other.date, datetime.date):
                        return -1
            elif not self.is_datetime() and not other.is_datetime():
                if not isinstance(self.date, datetime.date) and not isinstance(other.date, datetime.date):
                    return 0
                elif isinstance(self.date, datetime.date) and not isinstance(other.date, datetime.date):
                    return 1
                elif not isinstance(self.date, datetime.date) and isinstance(other.date, datetime.date):
                    return -1
            return cmp(self.date, other.date)
        else:
            if not other:
                return 1
        return 0
