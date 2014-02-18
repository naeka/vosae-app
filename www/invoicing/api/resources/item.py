# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import (
    TenantResource,
    RestorableMixinResource
)
from invoicing.models import Item
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'ItemResource',
)


class ItemResource(RestorableMixinResource, TenantResource):
    reference = base_fields.CharField(
        attribute='reference',
        help_text=HELP_TEXT['item']['reference']
    )
    description = base_fields.CharField(
        attribute='description',
        help_text=HELP_TEXT['item']['description']
    )
    unit_price = base_fields.DecimalField(
        attribute='unit_price',
        help_text=HELP_TEXT['item']['unit_price']
    )
    type = base_fields.CharField(
        attribute='type',
        help_text=HELP_TEXT['item']['type']
    )

    currency = fields.ReferenceField(
        to='invoicing.api.resources.CurrencyResource',
        attribute='currency',
        null=True,
        help_text=HELP_TEXT['item']['currency']
    )
    tax = fields.ReferenceField(
        to='invoicing.api.resources.TaxResource',
        attribute='tax',
        null=True,
        help_text=HELP_TEXT['item']['tax']
    )

    class Meta(TenantResource.Meta):
        queryset = Item.objects.all()
        excludes = ('tenant',)
