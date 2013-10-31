# -*- coding: utf-8 -*-

from south.v2 import DataMigration
from organizer.models import VosaeCalendar, CalendarList, VosaeEvent


class Migration(DataMigration):

    def forwards(self, orm):
        # VosaeCalendar
        for vosae_calendar in VosaeCalendar.objects():
            vosae_calendar._changed_fields = ['tenant']
            vosae_calendar.acl._changed_fields = ['read_list', 'write_list', 'negate_list']
            for idx, rule in enumerate(vosae_calendar.acl.rules):
                vosae_calendar.acl.rules[idx]._changed_fields = ['principal']
            vosae_calendar.save()

        # CalendarList
        for calendar_list in CalendarList.objects():
            calendar_list._changed_fields = ['tenant', 'vosae_user', 'calendar']
            calendar_list.save()

        # VosaeEvent
        for vosae_event in VosaeEvent.objects():
            vosae_event._changed_fields = ['tenant', 'calendar', 'creator', 'organizer']
            for idx, attendee in enumerate(vosae_event.attendees):
                vosae_event.attendees[idx]._changed_fields = ['vosae_user']
            vosae_event.save()

    def backwards(self, orm):
        # Same ops, handled on save
        self.forwards(orm)

    models = {

    }

    complete_apps = ['organizer']
    symmetrical = True
