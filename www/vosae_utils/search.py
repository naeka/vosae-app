# -*- coding:Utf-8 -*-

from django.conf import settings

from pyes import ES
from pyes.helpers import SettingsBuilder
from pyes.mappings import DocumentObjectField

import inspect
import sys


__all__ = (
    'SearchDocumentMixin',
    'get_search_models',
    'get_search_settings'
)


# Cache search models
SEARCH_SETTINGS = None


class VosaeSettingsBuilder(SettingsBuilder):

    def as_dict(self):
        """Returns a dict"""
        return {
            "settings": self.settings,
            "mappings": dict((k, v.as_dict() if not isinstance(v, dict) and hasattr(v, "as_dict") else v) for k, v in self.mappings.iteritems())
        }


class SearchDocumentMixin(object):

    """
    Mixin for search documents.
    Boosting approach:
    - 3.0: main field
    - 2.0: secondary field
    - 1.5: third field if important else 1.0
    - 0.8: non important fields
    """

    class Meta(object):
        document_type = None
        fields = []

    @classmethod
    def get_indexable_documents(cls, **kwargs):
        return cls.objects.filter(**kwargs)

    def get_search_kwargs(self):
        raise NotImplementedError("Model %s must implement `get_search_kwargs()` method" % self.Meta.document_type)

    def es_index(self):
        conn = ES(settings.ES_SERVERS, basic_auth=settings.ES_AUTH)
        conn.index(
            doc=self.get_search_kwargs(),
            index=self.tenant.slug,
            doc_type=self.Meta.document_type,
            id=unicode(self.id)
        )

    def es_deindex(self):
        conn = ES(settings.ES_SERVERS, basic_auth=settings.ES_AUTH)
        try:
            conn.delete(
                index=self.tenant.slug,
                doc_type=self.Meta.document_type,
                id=meta.id
            )
        except:
            pass


def get_search_models():
    search_models = []
    for app in settings.VOSAE_APPS:
        try:
            members = inspect.getmembers(sys.modules[app + '.models'], inspect.isclass)
        except KeyError:
            continue
        for name, obj in members:
            if issubclass(obj, SearchDocumentMixin) and obj is not SearchDocumentMixin:
                search_models.append((name, obj))
    return search_models


def get_search_settings():
    global SEARCH_SETTINGS

    # Use cached search settings if available
    if SEARCH_SETTINGS is not None:
        return SEARCH_SETTINGS

    # Process search settings
    search_models = get_search_models()
    SEARCH_SETTINGS = VosaeSettingsBuilder(settings=settings.ES_SETTINGS)
    for name, obj in search_models:
        docmapping = DocumentObjectField(_all=settings.ES_ALL_CONFIG, name=obj.Meta.document_type)
        for field in obj.Meta.fields:
            docmapping.add_property(field)
        SEARCH_SETTINGS.add_mapping(docmapping, obj.Meta.document_type)
    return SEARCH_SETTINGS
