# -*- coding:Utf-8 -*-

from mongoengine import Document, fields

from vosae_utils import SearchDocumentMixin
from pyes import mappings as search_mappings

from core.tasks import es_document_index, es_document_deindex
from core.mixins import RestorableMixin
from invoicing import ITEM_TYPES


__all__ = ('Item',)


class Item(RestorableMixin, Document, SearchDocumentMixin):

    """An item represents an invoicable product or service."""
    TYPES = ITEM_TYPES

    tenant = fields.ReferenceField("Tenant", required=True)
    reference = fields.StringField(required=True, unique_with="tenant", regex=r"^[a-zA-Z0-9_-]+$", max_length=32)
    description = fields.StringField(required=True, max_length=512)
    unit_price = fields.DecimalField(required=True)
    currency = fields.ReferenceField("Currency", required=True)
    tax = fields.ReferenceField("Tax", required=True)
    type = fields.StringField(required=True, choices=TYPES, default="PRODUCT")

    meta = {
        "indexes": ["tenant", "reference"],

        # Vosae specific
        "vosae_permissions": ("see_item", "add_item", "change_item", "delete_item"),
        "vosae_mandatory_permissions": ("invoicing_access",),
    }

    class Meta:
        document_type = 'item'
        document_boost = 1
        fields = [
            search_mappings.StringField(name="reference", boost=document_boost * 3.0, index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="description", boost=document_boost * 1.8, index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="type", index="not_analyzed", term_vector="with_positions_offsets", include_in_all=False),
        ]

    def __unicode__(self):
        return self.reference or u"Item object"

    def get_search_kwargs(self):
        return {
            'reference': self.reference,
            'description': self.description,
            'type': self.type
        }

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        """
        Post save hook handler

        - Index item in elasticsearch
        """
        # Index item in elasticsearch
        es_document_index.delay(document)

    @classmethod
    def post_delete(self, sender, document, **kwargs):
        """
        Post save hook handler

        - De-index item from elasticsearch
        """
        # De-index item from elasticsearch
        es_document_deindex.delay(document)
