# -*- coding:Utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.timezone import now
import uuid
import hmac

try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha


__all__ = (
    'ApiKey',
)


class ApiKey(models.Model):

    """ApiKeys are simple identifiers used to both authenticate and identify clients"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='api_keys')
    label = models.CharField(max_length=256)
    key = models.CharField(max_length=256, blank=True, default='', db_index=True)
    created_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('user', 'label')
        app_label = 'account'

    def __unicode__(self):
        return u'{0} for {1}'.format(self.key, self.user)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()

        return super(ApiKey, self).save(*args, **kwargs)

    def generate_key(self):
        # Get a random UUID.
        new_uuid = uuid.uuid4()
        # Hmac that beast.
        return hmac.new(str(new_uuid), digestmod=sha1).hexdigest()
