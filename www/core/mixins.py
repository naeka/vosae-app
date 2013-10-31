# -*- coding:Utf-8 -*-

from mongoengine import fields, signals


__all__ = (
    'ZombieMixin',
)


class ZombieMixin(object):
    STATUSES = ('ACTIVE', 'INACTIVE')
    DEFAULT_STATUS = 'ACTIVE'
    DELETE_STATUS = 'INACTIVE'

    status = fields.StringField(choices=STATUSES, required=True, default=DEFAULT_STATUS)

    def delete(self, force=False, *args, **kwargs):
        """
        A :class:`~core.models.ZombieMixin` cannot be deleted: a lot of objects
        refers to this. On delete, a specific status is applied.
        """
        if force:
            super(ZombieMixin, self).delete(*args, **kwargs)
        else:
            self.status = self.DELETE_STATUS
            self.update(set__status=self.status)
            signals.post_delete.send(self.__class__, document=self)


class AsyncTTLUploadsMixin(object):
    RELATED_WITH_TTL = []

    def remove_related_ttl(self):
        def remove_ttl(related_file):
            if related_file and getattr(related_file, 'ttl', None):
                related_file.update(unset__ttl=1, unset__delete_after=1)

        for related in self.RELATED_WITH_TTL:
            related = getattr(self, related)
            if isinstance(related, list):
                for related_file in related:
                    remove_ttl(related_file)
            else:
                remove_ttl(related)
