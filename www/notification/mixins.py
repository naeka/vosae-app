# -*- coding:Utf-8 -*-

from mongoengine import fields


__all__ = (
    'NotificationAwareDocumentMixin',
    'NotificationAwareResourceMixin'
)


class NotificationAwareDocumentMixin(object):
    subscribers = fields.ListField(fields.ReferenceField("VosaeUser"))


class NotificationAwareResourceMixin(object):

    def full_hydrate(self, bundle):
        """Add request issuer to subscribers set if not already present"""
        bundle = super(NotificationAwareResourceMixin, self).full_hydrate(bundle)
        if bundle.request.vosae_user not in bundle.obj.subscribers:
            bundle.obj.subscribers.append(bundle.request.vosae_user)
        return bundle
