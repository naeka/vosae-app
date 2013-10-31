# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields
from core.api.utils import TenantResource

from organizer.models import CalendarList
from organizer.api.doc import HELP_TEXT


__all__ = (
    'CalendarListResource',
)


class CalendarListResource(TenantResource):
    summary = base_fields.CharField(
        attribute='calendar__summary',
        readonly=True,
        help_text=HELP_TEXT['vosae_calendar']['summary']
    )
    description = base_fields.CharField(
        attribute='calendar__description',
        null=True,
        readonly=True,
        help_text=HELP_TEXT['vosae_calendar']['description']
    )
    location = base_fields.CharField(
        attribute='calendar__location',
        null=True,
        readonly=True,
        help_text=HELP_TEXT['vosae_calendar']['location']
    )
    timezone = base_fields.CharField(
        attribute='calendar__timezone',
        readonly=True,
        help_text=HELP_TEXT['vosae_calendar']['timezone']
    )
    summary_override = base_fields.CharField(
        attribute='summary_override',
        null=True,
        blank=True,
        help_text=HELP_TEXT['calendar_list']['summary_override']
    )
    color = base_fields.CharField(
        attribute='color',
        blank=True,
        help_text=HELP_TEXT['calendar_list']['color']
    )
    selected = base_fields.BooleanField(
        attribute='selected',
        blank=True,
        help_text=HELP_TEXT['calendar_list']['selected']
    )
    is_own = base_fields.BooleanField(
        readonly=True,
        help_text=HELP_TEXT['calendar_list']['is_own']
    )

    calendar = fields.ReferenceField(
        to='organizer.api.resources.VosaeCalendarResource',
        attribute='calendar',
        help_text=HELP_TEXT['calendar_list']['calendar']
    )

    reminders = fields.EmbeddedListField(
        of='organizer.api.resources.ReminderEntryResource',
        attribute='reminders',
        null=True,
        blank=True,
        full=True,
        help_text=HELP_TEXT['calendar_list']['reminders']
    )

    class Meta(TenantResource.Meta):
        resource_name = 'calendar_list'
        queryset = CalendarList.objects.all()
        excludes = ('tenant', 'vosae_user')
        filtering = {
            'calendar': ('exact',)
        }

    def get_object_list(self, request):
        """Filters objects on current user (extracted from request)"""
        object_list = super(CalendarListResource, self).get_object_list(request)
        return object_list.filter(vosae_user=request.vosae_user)

    def hydrate(self, bundle):
        """Automatically set the user (extracted from request)"""
        bundle = super(CalendarListResource, self).hydrate(bundle)
        bundle.obj.vosae_user = bundle.request.vosae_user
        return bundle

    def dehydrate_is_own(self, bundle):
        """`is_own` is processed here, based on the request's user"""
        try:
            if bundle.obj.calendar.acl.get_owner() == bundle.request.vosae_user:
                return True
        except:
            pass
        return False
