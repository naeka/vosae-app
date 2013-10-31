# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie.authorization import Authorization
from tastypie_mongoengine import fields

from core.api.utils import VosaeResource
from invoicing.models import Currency
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'CurrencyResource',
)


class CurrencyResource(VosaeResource):
    symbol = base_fields.CharField(
        attribute='symbol',
        help_text=HELP_TEXT['currency']['symbol']
    )

    rates = fields.EmbeddedListField(
        of='invoicing.api.resources.ExchangeRateResource',
        attribute='rates',
        readonly=True,
        full=True,
        help_text=HELP_TEXT['currency']['rates']
    )

    class Meta(VosaeResource.Meta):
        queryset = Currency.objects.all()
        authorization = Authorization()
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        filtering = {
            "symbol": ('exact',)
        }
