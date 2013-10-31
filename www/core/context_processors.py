# -*- coding:Utf-8 -*-

from django.conf import settings


def vosae_settings(context):
    return {
        "VOSAE_SUPPORTED_CURRENCIES": settings.VOSAE_SUPPORTED_CURRENCIES,
        "VOSAE_SUPPORTED_COUNTRIES": settings.VOSAE_SUPPORTED_COUNTRIES,
        "SENTRY_DSN": settings.SENTRY_DSN,
        "PUSHER_KEY": getattr(settings, 'PUSHER_KEY', None)
    }


def debug(context):
    return {'DEBUG': settings.DEBUG}


def travis(context):
    return {'TRAVIS': settings.TRAVIS}


def site(context):
    return {'site': {'name': settings.SITE_NAME, 'url': settings.SITE_URL}}
