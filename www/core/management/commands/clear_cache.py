# -*- coding:Utf-8 -*-

from django.core.cache import get_cache
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    """A simple management command which clears the given cache."""
    help = 'Fully clear your given cache.'

    def handle(self, *args, **kwargs):
        try:
            cache = get_cache(str(args[0]))
            cache.clear()
            self.stdout.write('The "%s" cache has been cleared!\n' % args[0])
        except AttributeError:
            raise CommandError('You have no cache configured!\n')
