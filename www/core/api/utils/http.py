# -*- coding:Utf-8 -*-

from tastypie import http


__all__ = (
    'VosaeHttpTooManyRequests',
)


class VosaeHttpTooManyRequests(http.HttpTooManyRequests):

    def __init__(self, *args, **kwargs):
        throttle_stats = kwargs.pop('throttle_stats', None)
        super(VosaeHttpTooManyRequests, self).__init__(*args, **kwargs)
        if throttle_stats:
            self['X-RateLimit-Remaining'] = throttle_stats.get('remaining')
            self['X-RateLimit-Limit'] = throttle_stats.get('limit')
