# -*- coding:Utf-8 -*-

from django.conf import settings
from mongoengine import EmbeddedDocument, fields


__all__ = ('ExchangeRate',)


class ExchangeRate(EmbeddedDocument):

    """
    Exchange rates are included in every :class:`~invoicing.models.Currency` objects.

    They represent the rate between two currencies at a specific time.
    """
    currency_to = fields.StringField(required=True, choices=settings.VOSAE_SUPPORTED_CURRENCIES)
    datetime = fields.DateTimeField(required=True)
    rate = fields.DecimalField(required=True)

    def __unicode__(self):
        return self.currency_to
