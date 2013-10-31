# -*- coding:Utf-8 -*-

from tastypie import bundle as tastypie_bundle, exceptions
from tastypie_mongoengine import fields


class SupportedCurrenciesListField(fields.ReferencedListField):

    is_related = False
    is_m2m = False

    def hydrate(self, bundle):
        return [b.obj for b in self.hydrate_m2m(bundle)]

    def dehydrate(self, bundle, for_list=True):
        the_m2ms = None

        if isinstance(self.attribute, basestring):
            the_m2ms = getattr(bundle.obj, self.attribute)
        elif callable(self.attribute):
            the_m2ms = self.attribute(bundle)

        if not the_m2ms:
            if not self.null:
                raise exceptions.ApiFieldError("The document %r has an empty attribute '%s' and does not allow a null value." % (bundle.obj, self.attribute))
            return []

        self.m2m_resources = []
        m2m_dehydrated = []

        # the_m2ms is a list, not a queryset
        for m2m in the_m2ms:
            m2m_resource = self.get_related_resource(m2m)
            m2m_bundle = tastypie_bundle.Bundle(obj=m2m, request=bundle.request)
            self.m2m_resources.append(m2m_resource)
            m2m_dehydrated.append(self.dehydrate_related(m2m_bundle, m2m_resource, for_list=for_list))

        return m2m_dehydrated
