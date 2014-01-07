# -*- coding:Utf-8 -*-

from django.conf import settings
from django.utils.timezone import now as datetime_now, is_naive, make_aware, make_naive, utc
from mongoengine import Document, fields
from mongoengine.queryset import QuerySet
from bson import ObjectId
from dateutil.rrule import rrulestr
from datetime import datetime, date, time, timedelta
from itertools import islice
import icalendar
import copy

from vosae_utils import SearchDocumentMixin
from pyes import mappings as search_mappings

from organizer.models.embedded import reminder
from organizer.models.embedded.event_occurrence import EventOccurrence
from organizer.models.embedded.event_date_time import EventDateTime
from organizer.tasks import update_calendar_ical_data, emit_reminders
from core.tasks import es_document_index, es_document_deindex


__all__ = (
    'DATERANGE_FILTERS',
    'VosaeEvent',
)


START_FILTERS = ('start', 'start__gte', 'start__gt')
END_FILTERS = ('end', 'end__lte', 'end__lt')
DATERANGE_FILTERS = START_FILTERS + END_FILTERS


class VosaeEventQuerySet(QuerySet):

    def __init__(self, document, collection):
        super(VosaeEventQuerySet, self).__init__(document, collection)
        self._load_instances = False
        self._current_event = None
        self._current_event_occurrences = []

    def __getitem__(self, key):
        if self._load_instances:
            it = self.__iter__()
            if isinstance(key, int):
                return list(islice(it, key, key + 1))[0]
            elif isinstance(key, slice):
                return list(islice(it, key.start, key.stop, key.step))
            raise AttributeError
        else:
            return super(VosaeEventQuerySet, self).__getitem__(key)

    def count(self):
        if self._load_instances:
            cnt = 0
            while True:
                try:
                    self.next()
                    cnt += 1
                except StopIteration:
                    break
            self.rewind()
            return cnt
        else:
            return super(VosaeEventQuerySet, self).count()

    def filter(self, *q_objs, **query):
        for filter_name, filter_query in query.iteritems():
            if filter_name in DATERANGE_FILTERS:
                query['occurrences__%s' % filter_name] = filter_query
                del query[filter_name]
        return super(VosaeEventQuerySet, self).filter(*q_objs, **query)

    def with_instances(self, start=None, end=None):
        """Retrieve all instances of events."""
        if start and not isinstance(start, datetime):
            raise ValueError('start must be None or datetime')
        if end and not isinstance(end, datetime):
            raise ValueError('end must be None or datetime')
        self._load_instances = True
        self._load_instances_start = start
        self._load_instances_end = end
        return self

    def next(self):
        """Wrap the result in a :class:`~mongoengine.Document` object."""
        # Iter over remaining occurrences of the event
        if self._current_event_occurrences:
            occurrence = self._current_event_occurrences.pop(0)
            event = copy.deepcopy(self._current_event)
            event.instance_id = occurrence.id
            if event.start.is_date():
                event.start.date = occurrence.start.date()
                event.end.date = occurrence.end.date()
            else:
                event.start.datetime = self._current_event_start_tz.fromutc(occurrence.start)
                event.end.datetime = self._current_event_end_tz.fromutc(occurrence.end)
            return event

        # Retrieve saved event in MongoDB
        self._current_event = super(VosaeEventQuerySet, self).next()
        if isinstance(self._current_event, VosaeEvent):
            self._current_event._regularize_timezones(from_utc=True)

        # Handle multiple instances spawning
        if self._load_instances:
            # Cache start/end timezones for occurrences spawning
            self._cache_tz()
            for occurrence in self._current_event.occurrences:
                if self._current_event.start == occurrence.start:
                    continue  # This is original start
                # Handle date request coverture
                if self._load_instances_start and self._load_instances_end:
                    if occurrence.end < self._load_instances_start or occurrence.start > self._load_instances_end:
                        continue
                elif self._load_instances_start:
                    if occurrence.end < self._load_instances_start:
                        continue
                elif self._load_instances_end:
                    if occurrence.start > self._load_instances_end:
                        continue
                # If not original and in period (if specified), append to occurrence list
                self._current_event_occurrences.append(occurrence)
            # If not in date request coverture, jumps to next occurrence
            if self._load_instances_start and self._load_instances_end:
                if self._current_event.end < self._load_instances_start or self._current_event.start > self._load_instances_end:
                    return self.next()
            elif self._load_instances_start:
                if self._current_event.end < self._load_instances_start:
                    return self.next()
            elif self._load_instances_end:
                if self._current_event.start > self._load_instances_end:
                    return self.next()
        return self._current_event

    def _cache_tz(self):
        """Cache event's start and end timezones"""
        try:
            self._current_event_start_tz = self._current_event.start.timezone.get_tz()
        except AttributeError:
            try:
                self._current_event_start_tz = self._current_event.calendar.timezone.get_tz()
            except AttributeError:
                self._current_event_start_tz = utc
        try:
            self._current_event_end_tz = self._current_event.end.timezone.get_tz()
        except AttributeError:
            try:
                self._current_event_end_tz = self._current_event.calendar.timezone.get_tz()
            except AttributeError:
                self._current_event_end_tz = utc


class VosaeEvent(Document, SearchDocumentMixin):
    STATUTES = (
        'CONFIRMED',
        'TENTATIVE',
        'CANCELLED'
    )
    TRANSPARENCIES = (
        'OPAQUE',
        'TRANSPARENT'
    )

    tenant = fields.ReferenceField("Tenant", required=True)
    calendar = fields.ReferenceField("VosaeCalendar", required=True)
    status = fields.StringField(choices=STATUTES)
    created_at = fields.DateTimeField(default=datetime_now, required=True)
    updated_at = fields.DateTimeField(required=True)
    summary = fields.StringField(required=True, max_length=64)
    description = fields.StringField(max_length=1024)
    location = fields.StringField(max_length=512)
    color = fields.StringField(regex=r'#[0-9a-fA-F]{6}$')
    creator = fields.ReferenceField("VosaeUser", required=True)
    organizer = fields.ReferenceField("VosaeUser", required=True)
    start = fields.EmbeddedDocumentField("EventDateTime", required=True, default=lambda: EventDateTime())
    end = fields.EmbeddedDocumentField("EventDateTime", required=True, default=lambda: EventDateTime())
    recurrence = fields.StringField()
    occurrences = fields.ListField(fields.EmbeddedDocumentField("EventOccurrence"), required=True)
    original_start = fields.EmbeddedDocumentField("EventDateTime", required=True)
    transparency = fields.StringField(choices=TRANSPARENCIES)
    attendees = fields.ListField(fields.EmbeddedDocumentField("Attendee"))
    reminders = fields.EmbeddedDocumentField("ReminderSettings", required=True, default=lambda: reminder.ReminderSettings())
    next_reminder = fields.EmbeddedDocumentField("NextReminder")
    ical_uid = fields.StringField(required=True)
    ical_data = fields.BinaryField(max_bytes=4096)

    meta = {
        "queryset_class": VosaeEventQuerySet,
        "indexes": ["tenant", "calendar", "occurrences.start", "occurrences.end"],
        "ordering": ["+occurrences.0.start"],

        # Vosae specific
        "vosae_mandatory_permissions": ("organizer_access",),
    }

    class Meta:
        document_type = 'event'
        document_boost = 0.9
        fields = [
            search_mappings.StringField(name="summary", boost=document_boost * 3.0, store=True, term_vector="with_positions_offsets", index="analyzed"),
            search_mappings.StringField(name="description", boost=document_boost * 2.0, store=True, term_vector="with_positions_offsets", index="analyzed"),
            search_mappings.StringField(name="location", boost=document_boost * 1.5, store=True, term_vector="with_positions_offsets", index="analyzed"),
        ]

    def get_search_kwargs(self):
        kwargs = {
            'summary': self.summary
        }
        if self.description:
            kwargs['description'] = self.description
        if self.location:
            kwargs['location'] = self.location
        return kwargs

    @classmethod
    def pre_save(self, sender, document, **kwargs):
        """
        Pre save hook handler

        - Preset ical uid (based on id)
        - Regularize timezones
        - Generates a list of the next occurrences
        - Schedule the next reminder occurrence
        - Set computed values/cache (original start, iCal data)
        """
        if not document.id:
            document.id = ObjectId()
            document.ical_uid = u'%s@%s' % (document.id, settings.VOSAE_DOMAIN)
        document._regularize_timezones()
        document._genere_occurrences()
        document._set_next_reminder()
        document.updated_at = datetime_now()
        document.original_start = document.start
        document.ical_data = document.to_ical()

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        """
        Post save hook handler

        - If next reminder in the timeframe, emits the task directly
        - Index event in elasticsearch
        - Update calendar iCal data
        """
        # If next reminder in the timeframe, emits the task directly
        document.check_immediate_reminders_emit()

        # Index event in elasticsearch
        es_document_index.delay(document)

        # Update calendar iCal data
        update_calendar_ical_data.delay(document.calendar)

    @classmethod
    def post_delete(self, sender, document, **kwargs):
        """
        Post delete hook handler

        - De-index event from elasticsearch
        """
        # De-index event from elasticsearch
        es_document_deindex.delay(document)

    def get_start_timezone(self):
        """
        Returns the start timezone.  
        Uses the calendar timezone if event's start timezone is not set
        """
        if self.start.timezone:
            return self.start.timezone.get_tz()
        else:
            return self.calendar.timezone.get_tz()

    def _regularize_timezones(self, from_utc=False):
        """Manage EventDateTime fields and ensure that all datetime are aware"""
        edt_fields = ('start', 'end')
        for field in edt_fields:
            edt = getattr(self, field)
            if not edt.datetime:
                continue
            if is_naive(edt.datetime):
                if edt.timezone:
                    tz = edt.timezone.get_tz()
                else:
                    tz = self.calendar.timezone.get_tz()
                if from_utc:
                    edt.datetime = tz.fromutc(edt.datetime)
                else:
                    edt.datetime = make_aware(edt.datetime, tz)
            setattr(self, field, edt)

    def _genere_occurrences(self):
        """Generate a list of occurrences."""
        if self.start.is_datetime() and self.end.is_datetime():
            delta = self.end.datetime - self.start.datetime
        elif self.start.is_date() and self.end.is_date():
            delta = self.end.date - self.start.date
        else:
            raise ValueError('datetime or date must be set for both start and end')
        self.occurrences = []
        if not self.recurrence:
            self.occurrences.append(self._create_occurrence(self.start.date_or_dt(), delta))
        else:
            rrs = shrink_rruleset(rrulestr(self.recurrence, dtstart=self.start.date_or_dt(), forceset=True))
            is_date = self.start.is_date()
            tz = self.get_start_timezone()
            for occurrence in rrs:
                # rruleset creates datetime objects
                if is_date:
                    if occurrence.time() == time():
                        # If time is 0, consider that occurrence is a date
                        occurrence = occurrence.date()
                    elif is_naive(occurrence):
                        # Else localize occurrence with event or calendar timezone
                        occurrence = tz.localize(occurrence)
                self.occurrences.append(self._create_occurrence(occurrence, delta))

    def _create_occurrence(self, start, delta):
        """
        Format each occurrence:  
        Generate an occurrence id from its start date/datetime.
        """
        if isinstance(start, datetime):
            utcstart = start.utctimetuple()
            occurrence_suffix = '{year:04d}{month:02d}{day:02d}T{hour:02d}{minute:02d}{second:02d}Z'.format(
                year=utcstart.tm_year,
                month=utcstart.tm_mon,
                day=utcstart.tm_mday,
                hour=utcstart.tm_hour,
                minute=utcstart.tm_min,
                second=utcstart.tm_sec
            )
        elif isinstance(start, date):
            occurrence_suffix = '{year:04d}{month:02d}{day:02d}'.format(
                year=start.year,
                month=start.month,
                day=start.day
            )
        else:
            raise AttributeError('start must be date or datetime')
        return EventOccurrence(
            id='{event_id}_{occurrence_suffix}'.format(
                event_id=self.id,
                occurrence_suffix=occurrence_suffix
            ),
            start=start,
            end=start + delta
        )

    def _get_next_occurrence(self, after=None):
        """
        Returns the next occurrence.  
        If `after` is not provided, use current the time
        """
        if not after:
            # Start of next minute prevents conflicts
            after = (datetime_now() + timedelta(minutes=1)).replace(second=0, microsecond=0)
        # If occurrences are dates (all-day), compares with date object
        if not isinstance(self.occurrences[0].start, datetime):
            after = after.date()
        for occurrence in self.occurrences:
            if after < occurrence.start:
                return occurrence.start

    def _get_next_reminder(self):
        """Returns the next reminder datetime and threshold"""
        from organizer.models import CalendarList
        # Get next occurrence
        next_occurrence = self._get_next_occurrence()
        if not next_occurrence:
            return None, None
        if type(next_occurrence) is date:
            tz = self.get_start_timezone()
            next_occurrence = tz.localize(datetime(next_occurrence.year, next_occurrence.month, next_occurrence.day))
        # Get a set of reminders threshold
        minutes_until = (next_occurrence - datetime_now()).total_seconds() / 60
        reminders = set([reminder.minutes for reminder in self.reminders.overrides if reminder.minutes < minutes_until])
        if self.reminders.use_default:
            for calendar_list in CalendarList.objects.filter(calendar=self.calendar):
                reminders.update([reminder.minutes for reminder in calendar_list.reminders if reminder.minutes < minutes_until])
        # Returns the closest reminder
        if reminders:
            next_in = max(reminders)
            return next_occurrence - timedelta(minutes=next_in), next_in
        return None, None

    def _set_next_reminder(self):
        next_dt, next_in = self._get_next_reminder()
        if next_dt:
            self.next_reminder = reminder.NextReminder(at=next_dt, threshold=next_in)
        else:
            self.next_reminder = None

    def check_immediate_reminders_emit(self):
        """Checks if the next reminder is in the timeframe and schedule its task if needed"""
        if self.next_reminder and self.next_reminder.at.date() == datetime_now().date():
            countdown = (self.next_reminder.at - datetime_now()).total_seconds()
            if countdown > 0:
                # Security check, avoiding potential infinite loop
                # Using countdown is also safer than eta because of timezones handling
                emit_reminders.apply_async(countdown=countdown, kwargs={'vosae_event_id': unicode(self.id)})

    def to_ical(self):
        """Generates an iCal formatted buffer of event's details"""
        vevent = icalendar.Event()
        vevent.add('uid', self.ical_uid)
        if self.status:
            vevent.add('status', self.status)
        vevent.add('created', self.created_at)
        vevent.add('last-modified', self.updated_at)
        vevent.add('summary', self.summary)
        if self.description:
            vevent.add('description', self.description)
        if self.location:
            vevent.add('location', self.location)
        organizer = icalendar.vCalAddress(u'MAILTO:%s' % self.organizer.email)
        organizer.params['CN'] = self.organizer.get_full_name() or ''
        vevent.add('organizer', organizer)
        vevent.add('dtstart', self.start.date_or_dt())
        vevent.add('dtend', self.end.date_or_dt())
        if self.transparency:
            vevent.add('transp', self.transparency)

        # Recurrences
        if self.recurrence:
            for recur in self.recurrence.splitlines():
                if recur.startswith('RRULE:'):
                    vrecur = icalendar.vRecur.from_ical(recur[6:])
                    vevent.add('rrule', vrecur)
                elif recur.startswith('EXRULE:'):
                    vrecur = icalendar.vRecur.from_ical(recur[7:])
                    vevent.add('exrule', vrecur)
                elif recur.startswith('RDATE:'):
                    vdddlist = icalendar.vDDDLists.from_ical(recur[6:])
                    vevent.add('rdate', vdddlist)
                elif recur.startswith('EXDATE:'):
                    vdddlist = icalendar.vDDDLists.from_ical(recur[7:])
                    vevent.add('exdate', vdddlist)

        # Attendees
        if self.attendees:
            for attendee in self.attendees:
                vattendee = icalendar.vCalAddress(u'MAILTO:%s' % attendee.email)
                if attendee.display_name:
                    vattendee.params['CN'] = attendee.display_name
                if attendee.optional:
                    vattendee.params['ROLE'] = 'OPT-PARTICIPANT'
                if attendee.optional is False:
                    vattendee.params['ROLE'] = 'REQ-PARTICIPANT'
                if attendee.optional is None:
                    vattendee.params['ROLE'] = 'NON-PARTICIPANT'
                if attendee.response_status:
                    vattendee.params['PARTSTAT'] = attendee.response_status
                if attendee.vosae_user:
                    vattendee.params['X-VOSAE-USER'] = unicode(attendee.vosae_user.id)
                vevent.add('attendee', vattendee)

        # Vosae specific
        vevent.add('x-vosae-creator', unicode(self.creator.id))
        vevent.add('x-vosae-event', unicode(self.id))
        return vevent.to_ical()


def shrink_rruleset(rruleset):
    """
    Ensure that an "infinite" rrule does not exceed the ORGANIZER_MAX_EVENT_OCCURRENCES
    setting. Default to 730 occurrences.
    """
    for i, rule in enumerate(rruleset._rrule):
        if not rruleset._rrule[i]._count or rruleset._rrule[i]._count > settings.ORGANIZER_MAX_EVENT_OCCURRENCES:
            rruleset._rrule[i]._count = settings.ORGANIZER_MAX_EVENT_OCCURRENCES
    for i, rule in enumerate(rruleset._exrule):
        if not rruleset._exrule[i]._count or rruleset._exrule[i]._count > settings.ORGANIZER_MAX_EVENT_OCCURRENCES:
            rruleset._exrule[i]._count = settings.ORGANIZER_MAX_EVENT_OCCURRENCES
    return rruleset
