# -*- coding:Utf-8 -*-

from django.conf import settings
from mongoengine import EmbeddedDocument, fields
from decimal import Decimal

from invoicing import CURRENCY_DISPLAY_SYMBOLS, currency_format


__all__ = ('SnapshotCurrency',)


class SnapshotCurrency(EmbeddedDocument):

    """A time-freezed :class:`~invoicing.models.Currency`"""
    DISPLAY_SYMBOLS = CURRENCY_DISPLAY_SYMBOLS

    symbol = fields.StringField(required=True, choices=settings.VOSAE_SUPPORTED_CURRENCIES)
    rates = fields.ListField(fields.EmbeddedDocumentField("ExchangeRate"), required=True)

    def __eq__(self, other):
        if isinstance(other, SnapshotCurrency) and self.symbol == other.symbol:
            return True
        return False

    def __unicode__(self):
        return self.symbol

    @property
    def display_symbol(self):
        """
        The *display symbol* associated to the currency (e.g. '€', '$', '£').

        The *symbol* attribute is in the iso4217 format (e.g. 'EUR', 'USD', 'GBP')
        """
        return self.DISPLAY_SYMBOLS[self.symbol]

    @staticmethod
    def currency_format(*args, **kwargs):
        return currency_format(*args, **kwargs)

    @staticmethod
    def convert(currency_from, currency_to, amount):
        from invoicing.models.currency import Currency
        base = Currency.objects.get(symbol=currency_from)
        return base.rate(currency_to).rate * Decimal(amount)

    def refresh_rates(self):
        """
        Refresh rates of the :class:`~invoicing.models.Currency` object.

        *Must only be used on embedded :class:`~invoicing.models.Currency` objects*
        """
        from invoicing.models.currency import Currency
        currency = Currency.objects.get(symbol=self.symbol)
        self.rates = currency.rates

    def to_currency(self, currency_to, amount):
        """
        Convert a given amount to a targetted currency.

        :param currency_to: iso4217 representation of the target currency
        :param amount: int/float/decimal value to be converted
        """
        return Decimal(amount) * self.rate(currency_to).rate

    def from_currency(self, currency_from, amount):
        """
        Convert a given amount from a source currency.

        :param currency_from: iso4217 representation of the source currency
        :param amount: int/float/decimal value to be converted
        """
        return Decimal(amount) / self.rate(currency_from).rate

    def rate(self, symbol):
        """
        Get the rate applied to a specific currency

        :param symbol: iso4217 representation of the target currency
        """
        for rate in self.rates:
            if rate.currency_to == symbol:
                return rate
