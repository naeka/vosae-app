# -*- coding:Utf-8 -*-

from tastypie.exceptions import ApiFieldError
from tastypie import fields as tastypie_fields, bundle as tastypie_bundle
from tastypie_mongoengine import fields


__all__ = (
    'ReferencedDictField',
)


class ReferencedDictField(tastypie_fields.DictField, tastypie_fields.RelatedField, fields.TastypieMongoengineMixin):

    def __init__(self, of, *args, **kwargs):
        return super(ReferencedDictField, self).__init__(to=of, *args, **kwargs)

    def dehydrate(self, bundle, for_list=True):
        the_m2ms = None

        if isinstance(self.attribute, basestring):
            the_m2ms = getattr(bundle.obj, self.attribute)
        elif callable(self.attribute):
            the_m2ms = self.attribute(bundle)

        if not the_m2ms:
            if not self.null:
                raise ApiFieldError("The document %r has an empty attribute '%s' and does not allow a null value." % (bundle.obj, self.attribute))
            return {}

        self.m2m_resources = {}
        m2m_dehydrated = {}

        # the_m2ms is a list, not a queryset
        for m2m_key, m2m_obj in the_m2ms.iteritems():
            m2m_resource = self.get_related_resource(m2m_obj)
            m2m_bundle = tastypie_bundle.Bundle(obj=m2m_obj, request=bundle.request)
            self.m2m_resources[m2m_key] = m2m_resource
            m2m_dehydrated[m2m_key] = self.dehydrate_related(m2m_bundle, m2m_resource, for_list=for_list)
        return m2m_dehydrated
