# -*- Coding:Utf-8 -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from pusher import Pusher as PusherAPI


__all__ = (
    'PUSHER_IS_CONFIGURED',
    'emit_to_channel',
    'pusher'
)


class Pusher(PusherAPI):

    def __init__(self, app_id=None, key=None, secret=None, **kwargs):
        if not hasattr(settings, "PUSHER_APP_ID") and app_id is None:
            raise ImproperlyConfigured("PUSHER_APP_ID must be set or app_id must be passed to Pusher")
        if not hasattr(settings, "PUSHER_KEY") and key is None:
            raise ImproperlyConfigured("PUSHER_KEY must be set or key must be passed to Pusher")
        if not hasattr(settings, "PUSHER_SECRET") and secret is None:
            raise ImproperlyConfigured("PUSHER_SECRET must be set or secret must be passed to Pusher")

        kw = {
            "app_id": settings.PUSHER_APP_ID,
            "key": settings.PUSHER_KEY,
            "secret": settings.PUSHER_SECRET,
            "host": settings.PUSHER_HOST
        }
        kw.update(kwargs)
        super(Pusher, self).__init__(**kw)


PUSHER_IS_CONFIGURED = getattr(settings, 'PUSHER_APP_ID', None) is not None and \
    getattr(settings, 'PUSHER_KEY', None) is not None and \
    getattr(settings, 'PUSHER_SECRET', None) is not None
pusher = Pusher() if PUSHER_IS_CONFIGURED else None


def emit_to_channel(channel, event, data):
    if PUSHER_IS_CONFIGURED:
        pusher[channel].trigger(event, data)
