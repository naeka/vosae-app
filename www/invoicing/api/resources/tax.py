# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields

from core.api.utils import TenantResource, RestorableMixinResource
from invoicing.models import Tax
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'TaxResource',
)


class TaxResource(RestorableMixinResource, TenantResource):
    name = base_fields.CharField(
        attribute='name',
        help_text=HELP_TEXT['tax']['name']
    )
    rate = base_fields.DecimalField(
        attribute='rate',
        help_text=HELP_TEXT['tax']['rate']
    )

    class Meta(TenantResource.Meta):
        queryset = Tax.objects.all()
        excludes = ('tenant',)

    def hydrate_rate(self, bundle):
        """Rate is immutable, on PUT, ensures that rate is equal to the initial value"""
        if bundle.request.method.lower() == 'put':
            bundle.data['rate'] = bundle.obj.rate
        return bundle

    def is_restorable(self):
        """
        Taxes are not (currently) restorable
        """
        return False
