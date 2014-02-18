# -*- coding:Utf-8 -*-

from mongoengine import fields, signals


__all__ = (
    'RestorableMixin',
)


class RestorableMixin(object):
    STATES = ('ACTIVE', 'DELETED')
    DEFAULT_STATE = 'ACTIVE'
    DELETE_STATE = 'DELETED'

    state = fields.StringField(choices=STATES, required=True, default=DEFAULT_STATE)

    def delete(self, force=False, *args, **kwargs):
        """
        A :class:`~core.models.RestorableMixin` cannot be deleted: a lot of objects
        refers to this. On delete, a specific state is applied.
        """
        if force:
            super(RestorableMixin, self).delete(*args, **kwargs)
        else:
            self.state = self.DELETE_STATE
            self.update(set__state=self.state)
            signals.post_delete.send(self.__class__, document=self)

    @classmethod
    def get_indexable_documents(cls, **kwargs):
        return cls.objects.filter(state__ne=cls.DELETE_STATE, **kwargs)


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
