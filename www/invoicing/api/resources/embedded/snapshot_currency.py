# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import VosaeResource
from invoicing.models import SnapshotCurrency, Currency
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'SnapshotCurrencyResource',
)


class SnapshotCurrencyResource(VosaeResource):
    symbol = base_fields.CharField(
        attribute='symbol',
        help_text=HELP_TEXT['currency']['symbol']
    )

    rates = fields.EmbeddedListField(
        of='invoicing.api.resources.ExchangeRateResource',
        attribute='rates',
        full=True,
        null=True,
        help_text=HELP_TEXT['currency']['rates']
    )

    class Meta(VosaeResource.Meta):
        object_class = SnapshotCurrency
        excludes = ('id',)

    def hydrate(self, bundle):
        """
        If an `id` is present in serialized data (data comes from a Currency and not a SnapshotCurrency),
        the currency is fetch and exchange rates are updated based on their current rates.
        """
        bundle = super(SnapshotCurrencyResource, self).hydrate(bundle)
        if 'id' in bundle.data:
            currency = Currency.objects.get(id=bundle.data.pop('id'))
            snapshot = currency.get_snapshot()
            bundle.data['symbol'] = snapshot.symbol
            bundle.data['rates'] = []
            for rate in snapshot.rates:
                bundle.data['rates'].append({
                    'currency_to': rate.currency_to,
                    'datetime': rate.datetime,
                    'rate': rate.rate
                })
        return bundle
