# -*- coding:Utf-8 -*-

from django.conf import settings
from collections import OrderedDict
from bson import DBRef, SON
from mongoengine import Document
from mongoengine.base import get_document
from mongoengine.fields import (
    StringField,
    DateTimeField,
    MapField,
    ReferenceField,
    GenericReferenceField,
    RECURSIVE_REFERENCE_CONSTANT
)
import datetime


__all__ = (
    'SlugField',
    'DateField',
    'NotPrivateReferenceField',
    'MultipleReferencesField',
    'LocalizedMapField'
)


class SlugField(StringField):

    def __init__(self, **kwargs):
        kwargs.update(regex=r'^[-\w]+$', max_length=kwargs.get('max_length', 50))
        super(SlugField, self).__init__(**kwargs)


class DateField(DateTimeField):

    def validate(self, value, **kwargs):
        if type(value) is not datetime.date:
            self.error(u'cannot parse date "%s"' % value)

    def to_python(self, value, **kwargs):
        if isinstance(value, datetime.datetime):
            return value.date()
        return value


class NotPrivateReferenceField(ReferenceField):

    """
    A field only allowing references that have a private attribute to True
    """

    def validate(self, value, **kwargs):
        super(NotPrivateReferenceField, self).validate(value, **kwargs)
        if getattr(value, 'private', None):  # In case of DBRef
            self.error(u'{0} can\'t be private'.format(value))


class MultipleReferencesField(GenericReferenceField):

    """
    A field allowing to reference different classes.
    """

    def __init__(self, document_types, **kwargs):
        if not document_types or not isinstance(document_types, (list, tuple)):
            self.error('document_types argument must be a list of document class or a string')
        for document_type in document_types:
            if not isinstance(document_type, basestring):
                if not issubclass(document_type, (Document, basestring)):
                    self.error('Argument to ReferenceField constructor must be a document class or a string')

        self.document_types_obj = list(document_types)
        super(MultipleReferencesField, self).__init__(**kwargs)

    @property
    def document_types(self):
        for idx, document_type in enumerate(self.document_types_obj):
            if isinstance(document_type, basestring):
                if document_type == RECURSIVE_REFERENCE_CONSTANT:
                    self.document_types_obj[idx] = self.owner_document
                else:
                    self.document_types_obj[idx] = get_document(document_type)
        return self.document_types_obj

    def validate(self, value):
        if not isinstance(value, tuple(self.document_types + [DBRef, dict, SON])):
            self.error('A MultipleReferencesField can only contain documents')

        if isinstance(value, (dict, SON)):
            if '_ref' not in value or '_cls' not in value:
                self.error('A MultipleReferencesField can only contain documents')
            elif not any(value['_cls'].endswith(document_type) for document_type in self.document_types):
                self.error('A MultipleReferencesField can only contain documents')

        # We need the id from the saved object to create the DBRef
        elif isinstance(value, Document) and value.id is None:
            self.error('You can only reference documents once they have been'
                       ' saved to the database')

    def to_mongo(self, document):
        """
        Need to use OrderedDict to ensure consistency
        """
        unordered = super(MultipleReferencesField, self).to_mongo(document)
        if isinstance(unordered, dict) and '_cls' in unordered and '_ref' in unordered:
            return OrderedDict(sorted(unordered.items()))
        else:
            return unordered


class LocalizedMapField(MapField):

    def validate(self, value, **kwargs):
        super(LocalizedMapField, self).validate(value, **kwargs)
        if any(k for k in value.keys() if k not in [l[0] for l in settings.LANGUAGES]):
            self.error('Invalid map key - documents must have only valid language keys')

    def to_python(self, value):
        """
        Checks that the referenced object still exists. Removes it otherwise.
        """
        objs = super(LocalizedMapField, self).to_python(value)
        for language, obj in objs.items():
            if self.field.document_type._get_db().dereference(obj) is None:
                del objs[language]
        return objs
