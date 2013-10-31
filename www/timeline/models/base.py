# -*- coding:Utf-8 -*-

from django.utils.timezone import now as datetime_now
from mongoengine import DynamicDocument, fields

from django.conf import settings
from realtime.utils import emit_to_channel


__all__ = (
    'TimelineEntry',
)


class TimelineEntry(DynamicDocument):
    tenant = fields.ReferenceField("Tenant", required=True)
    issuer = fields.ReferenceField("VosaeUser")
    module = fields.StringField(choices=settings.VOSAE_MODULES, required=True)
    datetime = fields.DateTimeField(required=True, default=datetime_now)
    access_permission = fields.StringField()
    see_permission = fields.StringField()

    meta = {
        "indexes": ["tenant", "access_permission", "see_permission"],
        "ordering": ["-id"],
        "allow_inheritance": True
    }

    @classmethod
    def post_save(self, sender, document, **kwargs):
        """
        Post save hook handler

        Emits timeline entry through the realtime service
        """
        from core.models import VosaeUser
        from timeline.api.resources import TimelineEntryResource
        ter = TimelineEntryResource()
        perms = []
        if document.access_permission:
            perms.append(document.access_permission)
        if document.see_permission:
            perms.append(document.see_permission)

        for user_id in VosaeUser.objects.filter(tenant=document.tenant, permissions__acquired__all=perms).values_list('id'):
            try:
                resource_type = ter._get_type_from_class(ter._meta.polymorphic, document.__class__)
            except:
                resource_type = None
            emit_to_channel(u'private-user-{0}'.format(unicode(user_id)), u'new-timeline-entry', {
                u'id': unicode(document.id),
                u'type': resource_type
            })
