# -*- coding:Utf-8 -*-

from django.utils.timezone import now as datetime_now
from mongoengine import DynamicDocument, fields
from realtime.utils import emit_to_channel


class Notification(DynamicDocument):
    tenant = fields.ReferenceField("Tenant", required=False)
    recipient = fields.ReferenceField("VosaeUser", required=True)
    issuer = fields.ReferenceField("VosaeUser")
    sent_at = fields.DateTimeField(required=True, default=datetime_now)
    read = fields.BooleanField(required=True, default=False)

    meta = {
        "indexes": ["tenant", "recipient", "sent_at", "read"],
        "ordering": ["-sent_at"],
        "allow_inheritance": True
    }

    @classmethod
    def post_save(self, sender, document, **kwargs):
        """
        Post save hook handler

        Emits notification through the realtime service
        """
        from notification.api.resources import NotificationResource
        nr = NotificationResource()
        try:
            resource_type = nr._get_type_from_class(nr._meta.polymorphic, document.__class__)
        except:
            resource_type = None
        emit_to_channel(u'private-user-{0}'.format(unicode(document.recipient.id)), u'new-notification', {
            u'id': unicode(document.id),
            u'type': resource_type
        })
