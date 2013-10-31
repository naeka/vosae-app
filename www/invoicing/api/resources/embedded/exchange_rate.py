# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields

from core.api.utils import VosaeResource
from invoicing.models import ExchangeRate
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'ExchangeRateResource',
)


class ExchangeRateResource(VosaeResource):
    currency_to = base_fields.CharField(
        attribute='currency_to',
        help_text=HELP_TEXT['exchange_rate']['currency_to']
    )
    datetime = base_fields.DateTimeField(
        attribute='datetime',
        help_text=HELP_TEXT['exchange_rate']['datetime']
    )
    rate = base_fields.DecimalField(
        attribute='rate',
        help_text=HELP_TEXT['exchange_rate']['rate']
    )

    class Meta(VosaeResource.Meta):
        object_class = ExchangeRate
        include_resource_uri = False
