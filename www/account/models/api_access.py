# -*- coding:Utf-8 -*-

from django.db import models


__all__ = (
    'ApiAccess',
)


class ApiAccess(models.Model):

    """A simple model for use with the ``CacheDBThrottle`` behaviors."""
    identifier = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, default='')
    request_method = models.CharField(max_length=10, blank=True, default='')
    accessed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'account'

    def __unicode__(self):
        return u'{0} @ {1}'.format(self.identifier, self.accessed_at)
