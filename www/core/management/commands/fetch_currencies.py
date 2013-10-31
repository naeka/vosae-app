# -*- coding:Utf-8 -*-

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    """A simple management command which fetch currencies rates."""
    help = 'Fetch currencies rates on OpenExchangeRates.'

    def handle(self, *args, **kwargs):
        from invoicing.models import Currency
        try:
            Currency.refresh_currencies()
            print "Done."
        except Exception as e:
            raise CommandError(e)
