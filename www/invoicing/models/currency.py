# -*- coding:Utf-8 -*-

from django.conf import settings
import json
from mongoengine import Document, fields
from decimal import Decimal
from bson.dbref import DBRef
import urllib2
import datetime

from invoicing import CURRENCY_DISPLAY_SYMBOLS, currency_format
from invoicing.models.embedded.snapshot_currency import SnapshotCurrency


__all__ = ('Currency',)


class Currency(Document):

    """Currencies are globals: they do not belongs to :class:`~core.models.Tenant`\ s."""
    DISPLAY_SYMBOLS = CURRENCY_DISPLAY_SYMBOLS

    symbol = fields.StringField(required=True, choices=settings.VOSAE_SUPPORTED_CURRENCIES)
    rates = fields.ListField(fields.EmbeddedDocumentField("ExchangeRate"))

    meta = {
        "indexes": ["symbol"],

        # Vosae specific
        "vosae_mandatory_permissions": ("invoicing_access",),
    }

    def __eq__(self, other):
        if isinstance(other, Currency) and self.symbol == other.symbol:
            return True
        elif isinstance(other, DBRef):
            if self.to_dbref() == other:
                return True
        return False

    def __unicode__(self):
        return self.symbol

    @property
    def display_symbol(self):
        """
        The display symbol associated to the currency (e.g. '€', '$', '£').

        The *symbol* attribute is in the iso4217 format (e.g. 'EUR', 'USD', 'GBP')
        """
        return self.DISPLAY_SYMBOLS[self.symbol]

    @staticmethod
    def currency_format(*args, **kwargs):
        return currency_format(*args, **kwargs)

    @staticmethod
    def refresh_currencies():
        """
        A :class:`~invoicing.models.Currency` contains rates which should be updated.

        This method allows tasks scripts to update currencies rates on a regular basis.
        """
        from invoicing.models import ExchangeRate
        base_currency = 'USD'
        currencies_symbols = [k[0] for k in settings.VOSAE_SUPPORTED_CURRENCIES]
        rates_uri = 'http://openexchangerates.org/latest.json?app_id={0}'.format(settings.OPEN_EXCHANGE_RATES_APP_ID)
        base_rates = json.loads(urllib2.urlopen(rates_uri).read())
        scrapped_dt = datetime.datetime.fromtimestamp(base_rates['timestamp']).replace(second=0)
        for symbol in currencies_symbols:
            try:
                currency = Currency.objects.get(symbol=symbol)
            except Currency.DoesNotExist:
                currency = Currency(symbol=symbol)
                for to_symbol in currencies_symbols:
                    if to_symbol == symbol:
                        continue
                    currency.rates.append(ExchangeRate(currency_to=to_symbol))
            for rate in currency.rates:
                rate.datetime = scrapped_dt
                if symbol == base_currency:
                    rate.rate = base_rates['rates'][rate.currency_to]
                else:
                    rate.rate = base_rates['rates'][rate.currency_to] / base_rates['rates'][symbol]
            currency.save(upsert=True)

    @staticmethod
    def convert(currency_from, currency_to, amount):
        """
        Convert a :class:`~invoicing.models.Currency` to another.
        Based on the current rates.
        """
        base = Currency.objects.get(symbol=currency_from)
        return base.rate(currency_to).rate * Decimal(amount)

    def to_currency(self, currency_to, amount):
        """
        Convert a :class:`~invoicing.models.Currency` to another.
        Based on the current rates.

        :param currency_to: iso4217 representation of the target currency
        :param amount: int/float/decimal value to be converted
        """
        return Decimal(amount) * self.rate(currency_to).rate

    def from_currency(self, currency_from, amount):
        """
        Convert a :class:`~invoicing.models.Currency` to another.
        Based on the current rates.

        :param currency_from: iso4217 representation of the source currency
        :param amount: int/float/decimal value to be converted
        """
        return Decimal(amount) / self.rate(currency_from).rate

    def rate(self, symbol):
        """
        Return the rate associated to the specified symbol.

        :param symbol: iso4217 representation of the target currency
        """
        for rate in self.rates:
            if rate.currency_to == symbol:
                return rate

    def get_snapshot(self):
        """Return the snapshot associated to the currency."""
        return SnapshotCurrency(symbol=self.symbol, rates=self.rates)
