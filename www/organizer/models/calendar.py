# -*- coding:Utf-8 -*-

from mongoengine import Document, fields
from django.conf import settings
import icalendar
import pytz

from organizer.fields import TimeZoneField
from organizer.models.embedded import CalendarAcl


__all__ = (
    'Calendar',
    'VosaeCalendar',
    'GoogleCalendar'
)


class Calendar(Document):

    """
    Represent a calendar on Vosae.

    Calendars are linked to Django users, not to :class:`~core.models.VosaeUser`\ s.
    """
    tenant = fields.ReferenceField("Tenant", required=True)

    meta = {
        "indexes": ["tenant"],
        "allow_inheritance": True,

        # Vosae specific
        "vosae_mandatory_permissions": ("organizer_access",),
    }


class VosaeCalendar(Calendar):

    """A wrapper to a Vosae calendar."""
    PRODID = '-//Vosae - %s//Vosae Calendar//EN' % settings.VOSAE_WWW_DOMAIN
    VERSION = '2.0'
    CALSCALE = 'GREGORIAN'
    DEFAULT_METHOD = 'PUBLISH'
    _events = None

    summary = fields.StringField(required=True, max_length=64)
    description = fields.StringField(max_length=1024)
    location = fields.StringField(max_length=256)
    timezone = TimeZoneField(required=True, choices=pytz.all_timezones, default=u'UTC')
    acl = fields.EmbeddedDocumentField("CalendarAcl", required=True, default=lambda: CalendarAcl())
    ical_data = fields.BinaryField()

    def __getstate__(self):
        self_dict = super(VosaeCalendar, self).__getstate__()
        self_dict['_events'] = None
        return self_dict

    def reload(self, *args, **kwargs):
        super(VosaeCalendar, self).reload(*args, **kwargs)
        self._events = None

    @property
    def events(self):
        from organizer.models.event import VosaeEvent
        if self._events is None and self.id is not None:
            self._events = VosaeEvent.objects.filter(calendar=self)
        return self._events

    @events.setter
    def events(self, value):
        pass

    @events.deleter
    def events(self, value):
        pass

    @classmethod
    def pre_save(self, sender, document, **kwargs):
        """
        Pre save hook handler

        - Computes ACL read/write list
        - Generates iCal data
        """
        document.acl.genere_rw_list()
        document.ical_data = document.to_ical()

    def to_ical(self, method=None):
        """Generates an iCal formatted list of calendar's events"""
        vcalendar = icalendar.Calendar()
        vcalendar.add('prodid', self.PRODID)
        vcalendar.add('version', self.VERSION)
        vcalendar.add('calscale', self.CALSCALE)
        vcalendar.add('method', method or self.DEFAULT_METHOD)
        vcalendar.add('x-wr-calname', self.summary)
        vcalendar.add('x-wr-timezone', self.timezone)
        if self.description:
            vcalendar.add('x-wr-caldesc', self.description)

        buf = vcalendar.to_ical().partition('END:VCALENDAR')
        try:
            events_data = ''.join(self.events.scalar('ical_data'))
        except:
            events_data = ''
        return buf[0] + events_data + buf[1] + buf[2]


class GoogleCalendar(Calendar):

    """
    A wrapper to a Google calendar.

    Calendar informations, events are grabbed using the **Google API**.

    **Not yet implemented**.
    """
    pass
