# -*- coding:Utf-8 -*-

from django.core.cache import get_cache
from tastypie.throttle import BaseThrottle
import time


__all__ = (
    'VosaeCacheThrottle',
    'VosaeCacheDBThrottle'
)

api_throttling_cache = get_cache('api_throttling')


class VosaeCacheThrottle(BaseThrottle):

    """
    A throttling mechanism that uses our dedicated API cache.

    Backported from tastypie
    """
    namespace = None

    def convert_identifier_to_key(self, identifier):
        key = super(VosaeCacheThrottle, self).convert_identifier_to_key(identifier)
        if self.namespace:
            key = "%s_%s" % (key, self.namespace)
        return key

    def should_be_throttled(self, identifier, **kwargs):
        key = self.convert_identifier_to_key(identifier)

        # Make sure something is there.
        api_throttling_cache.add(key, [])

        # Weed out anything older than the timeframe.
        minimum_time = int(time.time()) - int(self.timeframe)
        times_accessed = [access for access in api_throttling_cache.get(key) if access >= minimum_time]
        api_throttling_cache.set(key, times_accessed, self.expiration)

        remaining = int(self.throttle_at) - len(times_accessed)
        return {
            'remaining': remaining,
            'limit': self.throttle_at
        }

    def accessed(self, identifier, **kwargs):
        key = self.convert_identifier_to_key(identifier)
        times_accessed = api_throttling_cache.get(key, [])
        times_accessed.append(int(time.time()))
        api_throttling_cache.set(key, times_accessed, self.expiration)


class VosaeCacheDBThrottle(VosaeCacheThrottle):

    """
    A throttling mechanism that uses our dedicated API cache for actual
    throttling but writes-through to the database.

    This is useful for tracking/aggregating usage through time, to possibly
    build a statistics interface or a billing mechanism.

    Backported from tastypie
    """

    def accessed(self, identifier, **kwargs):
        # Do the import here, instead of top-level, so that the model is
        # only required when using this throttling mechanism.
        from account.models import ApiAccess
        super(VosaeCacheDBThrottle, self).accessed(identifier, **kwargs)
        # Write out the access to the DB for logging purposes.
        ApiAccess.objects.create(
            identifier=identifier,
            url=kwargs.get('url', ''),
            request_method=kwargs.get('request_method', '')
        )
