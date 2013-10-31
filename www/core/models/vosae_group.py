# -*- coding:Utf-8 -*-

from mongoengine import Document, fields
from django.utils.timezone import now as datetime_now

from vosae_utils import SearchDocumentMixin
from pyes import mappings as search_mappings

from core.models.embedded.vosae_permissions import VosaePermissions
from core.exceptions import AdministratorGroupIsImmutable
from core.tasks import es_document_index, es_document_deindex


__all__ = (
    'VosaeGroup',
)


class VosaeGroup(Document, SearchDocumentMixin):

    """
    A group to organize :class:`~core.models.Tenant`\ 's permissions.
    """
    tenant = fields.ReferenceField("Tenant", required=True)
    name = fields.StringField(unique_with="tenant", max_length=64)
    created_by = fields.ReferenceField("VosaeUser")
    created_at = fields.DateTimeField(required=True, default=datetime_now)
    is_admin = fields.BooleanField(required=True, default=False)
    permissions = fields.EmbeddedDocumentField("VosaePermissions", default=lambda: VosaePermissions())

    meta = {
        "indexes": ["tenant"],

        # Vosae specific
        "vosae_permissions": ("see_vosaegroup", "add_vosaegroup", "change_vosaegroup", "delete_vosaegroup"),
        "vosae_mandatory_permissions": ("core_access", "change_appconf"),
    }

    class Meta():
        document_type = 'group'
        document_boost = 2 / 3.0
        fields = [
            search_mappings.StringField(name="name", boost=document_boost * 3.0, store=True, term_vector="with_positions_offsets", index="analyzed"),
        ]

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.tenant)

    def get_search_kwargs(self):
        return {
            'name': self.name
        }

    @classmethod
    def pre_save(self, sender, document, **kwargs):
        """
        Pre save hook handler

        - Refresh group's permissions cache
        """
        document.permissions.refresh_acquired()

    @classmethod
    def post_save(self, sender, document, **kwargs):
        """
        Post save hook handler

        - Refresh all related :class:`~core.models.VosaeUser` permissions.  
          Occurs in a delayed task.
        - Index group in elasticsearch
        """
        from core.tasks import cache_changed_permissions
        cache_changed_permissions.delay(document)

        # Index group in elasticsearch
        es_document_index.delay(document)

    @classmethod
    def post_delete(self, sender, document, **kwargs):
        """
        Post delete hook handler

        - De-index group from elasticsearch
        """
        es_document_deindex.delay(document)

    def save(self, force=False, *args, **kwargs):
        """
        Prevent save of the "admin" group. It is immutable by default.
        """
        if not self._created and self.is_admin and not force:
            raise AdministratorGroupIsImmutable()
        super(VosaeGroup, self).save(*args, **kwargs)

    def delete(self, force=False, *args, **kwargs):
        """
        Prevent deletion of the "admin" group. It is immutable by default.
        """
        if self.is_admin and not force:
            raise AdministratorGroupIsImmutable()
        super(VosaeGroup, self).delete(*args, **kwargs)
