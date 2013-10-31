# -*- coding:Utf-8 -*-

from tastypie_mongoengine.resources import MongoEngineModelDeclarativeMetaclass


__all__ = (
    'VosaeModelDeclarativeMetaclass',
)


class VosaeModelDeclarativeMetaclass(MongoEngineModelDeclarativeMetaclass):

    def __new__(self, name, bases, attrs):
        new_class = super(VosaeModelDeclarativeMetaclass, self).__new__(self, name, bases, attrs)
        if 'id' in new_class.base_fields:
            new_class.base_fields['id'].help_text = 'Unique identifier of the resource'
            new_class.base_fields['id'].readonly = True
        if 'resource_uri' in new_class.base_fields:
            new_class.base_fields['resource_uri'].help_text = 'URI which represent a specific resource. All references are based upon this scheme'
        if 'resource_type' in new_class.base_fields:
            new_class.base_fields['resource_type'].help_text = 'Type of the resource. Used with polymorphic resources. Refers to the "resource_types" list to provide an expected type'
        return new_class
