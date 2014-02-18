# -*- coding:Utf-8 -*-

from mongoengine import Document, fields
from django_gravatar.helpers import get_gravatar_url

from core.mixins import RestorableMixin, AsyncTTLUploadsMixin
from notification.mixins import NotificationAwareDocumentMixin
from core.tasks import es_document_index, es_document_deindex


__all__ = (
    'Entity',
)


class Entity(RestorableMixin, Document, AsyncTTLUploadsMixin, NotificationAwareDocumentMixin):

    """A base class for :class:`~contacts.models.Contact` and :class:`~contacts.models.Organization`."""
    RELATED_WITH_TTL = ['photo']

    tenant = fields.ReferenceField("Tenant", required=True)
    creator = fields.ReferenceField("VosaeUser", required=True)
    private = fields.BooleanField(required=True, default=False)
    photo_source = fields.StringField(choices=["LOCAL", "GRAVATAR"])
    photo = fields.ReferenceField("VosaeFile")
    gravatar_mail = fields.EmailField(max_length=128)
    note = fields.StringField(max_length=2048)
    addresses = fields.ListField(fields.EmbeddedDocumentField("Address"))
    emails = fields.ListField(fields.EmbeddedDocumentField("Email"))
    phones = fields.ListField(fields.EmbeddedDocumentField("Phone"))
    invoicing_settings = {}  # fields.ReferenceField("InvoicingSettings")

    meta = {
        "indexes": ["tenant"],
        "allow_inheritance": True,

        # Vosae Specific
        "vosae_permissions": ("see_contact", "add_contact", "change_contact", "delete_contact"),
        "vosae_mandatory_permissions": ("contacts_access",),
        "vosae_timeline_permission": "see_contact",
        "forced_class_name": "contact",
    }

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        """
        Post save hook handler
        
        - Removes related TTL
        - Index entity in elasticsearch
        """
        # Removes related TTL
        document.remove_related_ttl()

        # Index entity in elasticsearch
        es_document_index.delay(document)

    @classmethod
    def post_delete(self, sender, document, **kwargs):
        """
        Post delete hook handler

        - Deletes related photo, if exists
        - De-index entity from elasticsearch
        """
        # Deletes related photo, if exists
        if document.photo:
            document.photo.delete()

        # De-index entity from elasticsearch
        es_document_deindex.delay(document)

    @property
    def photo_uri(self):
        """Return the photo URI or the default *empty* picture."""
        if self.photo_source:
            if self.photo_source == "LOCAL":
                try:
                    return self.photo.stream_link
                except:
                    return None
            if self.photo_source == "GRAVATAR":
                return get_gravatar_url(self.gravatar_mail)
        else:
            return None
