# -*- coding:Utf-8 -*-

from mongoengine import Q
from tastypie import fields as base_fields
from tastypie_mongoengine import fields
from core.api.utils import TenantResource

from organizer.models import VosaeCalendar
from organizer.api.doc import HELP_TEXT


__all__ = (
    'VosaeCalendarResource',
)


class VosaeCalendarResource(TenantResource):
    summary = base_fields.CharField(
        attribute='summary',
        help_text=HELP_TEXT['vosae_calendar']['summary']
    )
    description = base_fields.CharField(
        attribute='description',
        null=True,
        blank=True,
        help_text=HELP_TEXT['vosae_calendar']['description']
    )
    location = base_fields.CharField(
        attribute='location',
        null=True,
        blank=True,
        help_text=HELP_TEXT['vosae_calendar']['location']
    )
    timezone = base_fields.CharField(
        attribute='timezone',
        blank=True,
        help_text=HELP_TEXT['vosae_calendar']['timezone']
    )

    acl = fields.EmbeddedDocumentField(
        embedded='organizer.api.resources.CalendarAclResource',
        attribute='acl',
        help_text=HELP_TEXT['vosae_calendar']['acl']
    )

    class Meta(TenantResource.Meta):
        resource_name = 'vosae_calendar'
        queryset = VosaeCalendar.objects.all()
        excludes = ('tenant', 'occurrences', 'ical_data')

    def get_object_list(self, request):
        """Filters calendars on current user and its groups (extracted from request)"""
        object_list = super(VosaeCalendarResource, self).get_object_list(request)
        principals = [request.vosae_user] + request.vosae_user.groups
        return object_list.filter(Q(acl__read_list__in=principals))
