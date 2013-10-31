# -*- coding:Utf-8 -*-

from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist
from tastypie import fields as base_fields, http
from tastypie.utils import trailing_slash
from tastypie.validation import Validation
from tastypie_mongoengine import fields
from dateutil.parser import parse

from core.api.utils import TenantResource

from organizer.models import VosaeEvent, DATERANGE_FILTERS
from organizer.api.doc import HELP_TEXT


__all__ = (
    'VosaeEventResource',
)


class EventValidation(Validation):

    def is_valid(self, bundle, request=None):
        from django.utils.timezone import is_naive
        errors = {}

        for field in ['start', 'end']:
            data = bundle.data.get(field)
            if not data.get('date', None) and not data.get('datetime', None):
                errors['__all__'] = ["One of 'date' and 'datetime' must be set."]
            elif data.get('date', None) and data.get('datetime', None):
                errors['__all__'] = ["Only one of 'date' and 'datetime' must be set. The 'date' field is used for all-day events."]
            elif data.get('datetime', None) and is_naive(parse(data.get('datetime'))) and not data.get('timezone', None):
                errors['datetime'] = ["A timezone offset is required if not specified in the 'timezone' field"]

        return errors


class VosaeEventResource(TenantResource):
    status = base_fields.CharField(
        attribute='status',
        null=True,
        blank=True,
        help_text=HELP_TEXT['vosae_event']['status']
    )
    created_at = base_fields.DateTimeField(
        attribute='created_at',
        readonly=True,
        help_text=HELP_TEXT['vosae_event']['created_at']
    )
    updated_at = base_fields.DateTimeField(
        attribute='updated_at',
        readonly=True,
        help_text=HELP_TEXT['vosae_event']['updated_at']
    )
    summary = base_fields.CharField(
        attribute='summary',
        help_text=HELP_TEXT['vosae_event']['summary']
    )
    description = base_fields.CharField(
        attribute='description',
        null=True,
        blank=True,
        help_text=HELP_TEXT['vosae_event']['description']
    )
    location = base_fields.CharField(
        attribute='location',
        null=True,
        blank=True,
        help_text=HELP_TEXT['vosae_event']['location']
    )
    color = base_fields.CharField(
        attribute='color',
        null=True,
        blank=True,
        help_text=HELP_TEXT['vosae_event']['color']
    )
    start = fields.EmbeddedDocumentField(
        embedded='organizer.api.resources.EventDateTimeResource',
        attribute='start',
        help_text=HELP_TEXT['vosae_event']['start']
    )
    end = fields.EmbeddedDocumentField(
        embedded='organizer.api.resources.EventDateTimeResource',
        attribute='end',
        help_text=HELP_TEXT['vosae_event']['end']
    )
    recurrence = base_fields.CharField(
        attribute='recurrence',
        null=True,
        blank=True,
        help_text=HELP_TEXT['vosae_event']['recurrence']
    )
    original_start = fields.EmbeddedDocumentField(
        embedded='organizer.api.resources.EventDateTimeResource',
        attribute='original_start',
        readonly=True,
        help_text=HELP_TEXT['vosae_event']['original_start']
    )
    instance_id = base_fields.CharField(
        attribute='instance_id',
        readonly=True,
        null=True,
        blank=True,
        help_text=HELP_TEXT['vosae_event']['instance_id']
    )
    transparency = base_fields.CharField(
        attribute='transparency',
        null=True,
        blank=True,
        help_text=HELP_TEXT['vosae_event']['transparency']
    )

    calendar = fields.ReferenceField(
        to='organizer.api.resources.VosaeCalendarResource',
        attribute='calendar',
        help_text=HELP_TEXT['vosae_event']['calendar']
    )
    creator = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='creator',
        readonly=True,
        help_text=HELP_TEXT['vosae_event']['creator']
    )
    organizer = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='organizer',
        readonly=True,
        help_text=HELP_TEXT['vosae_event']['organizer']
    )
    attendees = fields.EmbeddedListField(
        of='organizer.api.resources.AttendeeResource',
        attribute='attendees',
        null=True,
        blank=True,
        full=True,
        help_text=HELP_TEXT['vosae_event']['attendees']
    )
    reminders = fields.EmbeddedDocumentField(
        embedded='organizer.api.resources.ReminderSettingsResource',
        attribute='reminders',
        blank=True,
        help_text=HELP_TEXT['vosae_event']['reminders']
    )

    class Meta(TenantResource.Meta):
        resource_name = 'vosae_event'
        queryset = VosaeEvent.objects.all()
        excludes = ('tenant', 'occurrences', 'next_reminder', 'ical_uid', 'ical_data')
        filtering = {
            'start': ('exact', 'gt', 'gte'),
            'end': ('exact', 'lt', 'lte'),
            'calendar': ('exact')
        }
        validation = EventValidation()

    def prepend_urls(self):
        """Add urls for resources actions."""
        urls = super(VosaeEventResource, self).prepend_urls()
        urls.extend((
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/instances%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('event_instances'), name='api_vosae_event_instances'),
        ))
        return urls

    def build_filters(self, filters=None):
        qs_filters = super(VosaeEventResource, self).build_filters(filters)
        for filter_name, filter_value in qs_filters.iteritems():
            if filter_name.endswith('__exact'):
                new_name = filter_name[:filter_name.index('__exact')]
                qs_filters[new_name] = filter_value
                del qs_filters[filter_name]
                filter_name = new_name
            if filter_name in DATERANGE_FILTERS:
                if isinstance(filter_value, basestring):
                    qs_filters[filter_name] = parse(filter_value)
        return qs_filters

    def get_object_list(self, request):
        """Filters events based on calendar accesses (extracted from request user)"""
        from organizer.models import VosaeCalendar
        object_list = super(VosaeEventResource, self).get_object_list(request)
        principals = [request.vosae_user] + request.vosae_user.groups
        calendars = VosaeCalendar.objects.filter(acl__read_list__in=principals, acl__negate_list__nin=principals)
        return object_list.filter(calendar__in=list(calendars))

    def apply_filters(self, request, applicable_filters):
        object_list = super(VosaeEventResource, self).apply_filters(request, applicable_filters)
        filters = request.GET
        if 'single_events' in filters and filters['single_events'] in ['true', 'True', True]:
            start = None
            end = None
            for filter_name, filter_value in filters.iteritems():
                try:
                    if filter_name.startswith('start'):
                        start = parse(filter_value)
                    elif filter_name.startswith('end'):
                        end = parse(filter_value)
                except:
                    pass
            return object_list.with_instances(start, end)
        return object_list

    def event_instances(self, request, **kwargs):
        """List all instances of the event"""
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        try:
            bundle = self.build_bundle(request=request)
            objects = self.obj_get_list(bundle, **self.remove_api_resource_names(kwargs)).with_instances()
        except ObjectDoesNotExist:
            return http.HttpNotFound()

        if objects.count() < 2:
            return http.HttpNotFound()

        sorted_objects = self.apply_sorting(objects, options=request.GET)

        first_objects_bundle = self.build_bundle(obj=objects[0], request=request)
        instances_resource_uri = '%sinstances/' % self.get_resource_uri(first_objects_bundle)
        paginator = self._meta.paginator_class(request.GET, sorted_objects, resource_uri=instances_resource_uri, limit=self._meta.limit)
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.
        bundles = [self.build_bundle(obj=obj, request=request) for obj in to_be_serialized['objects']]
        to_be_serialized['objects'] = [self.full_dehydrate(b) for b in bundles]
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)

    def full_hydrate(self, bundle):
        """Set event's creator and organizer"""
        bundle = super(VosaeEventResource, self).full_hydrate(bundle)
        bundle.obj.creator = bundle.request.vosae_user
        # Organizer should be the user owner of the calendar
        try:
            organizer = bundle.obj.calendar.acl.get_owner()
        except:
            organizer = bundle.request.vosae_user
        bundle.obj.organizer = organizer
        return bundle

    def full_dehydrate(self, bundle, for_list=False):
        bundle = super(VosaeEventResource, self).full_dehydrate(bundle, for_list=for_list)
        if not bundle.data['instance_id']:
            del bundle.data['instance_id']
        return bundle

    def dehydrate(self, bundle):
        """Dehydrates the appropriate CalendarList which differs according to user (extracted from request)"""
        from organizer.models import CalendarList
        from organizer.api.resources import CalendarListResource
        bundle = super(VosaeEventResource, self).dehydrate(bundle)
        calendar_list = CalendarList.objects.get(calendar=bundle.obj.calendar, vosae_user=bundle.request.vosae_user)
        calendar_list_resource = CalendarListResource()
        calendar_list_resource_bundle = calendar_list_resource.build_bundle(obj=calendar_list, request=bundle.request)
        bundle.data['calendar_list'] = calendar_list_resource.get_resource_uri(calendar_list_resource_bundle)
        return bundle
