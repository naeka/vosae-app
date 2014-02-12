# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import TenantResource
from notification.models import Notification
from notification.api.doc import HELP_TEXT


__all__ = (
    'NotificationBaseResource',
)


class NotificationBaseResource(TenantResource):
    sent_at = base_fields.DateTimeField(
        attribute='sent_at',
        readonly=True,
        help_text=HELP_TEXT['notification_base']['sent_at']
    )
    read = base_fields.BooleanField(
        attribute='read',
        readonly=True,
        help_text=HELP_TEXT['notification_base']['read']
    )

    issuer = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='issuer',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['notification_base']['issuer']
    )

    class Meta(TenantResource.Meta):
        object_class = Notification
        excludes = ('tenant', 'recipient')
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)

    def get_object_list(self, request):
        """Filters the notifications list on the recipient (extracted from request)"""
        return super(NotificationBaseResource, self).get_object_list(request).filter(recipient=request.vosae_user)
