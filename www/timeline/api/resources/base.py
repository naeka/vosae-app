# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields
from core.api.utils import TenantResource
from timeline.models import TimelineEntry
from timeline.api.doc import HELP_TEXT


__all__ = (
    'TimelineEntryBaseResource',
)


class TimelineEntryBaseResource(TenantResource):
    module = base_fields.CharField(
        attribute='module',
        help_text=HELP_TEXT['timeline_entry']['module']
    )
    datetime = base_fields.DateTimeField(
        attribute='datetime',
        help_text=HELP_TEXT['timeline_entry']['datetime']
    )
    issuer_name = base_fields.CharField(
        attribute='issuer__get_full_name',
        help_text=HELP_TEXT['entity_saved']['contact'],
        null=True,
    )

    issuer = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='issuer',
        blank=True,
        null=True,
        help_text=HELP_TEXT['timeline_entry']['issuer']
    )

    class Meta(TenantResource.Meta):
        object_class = TimelineEntry
        excludes = ('tenant', 'access_permission', 'see_permission')
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)

    def get_object_list(self, request):
        object_list = super(TimelineEntryBaseResource, self).get_object_list(request)
        if request and getattr(request, 'vosae_user', None):
            return object_list.filter(
                access_permission__in=request.vosae_user.permissions.access_perms,
                see_permission__in=request.vosae_user.permissions.see_perms
            )
        return object_list
