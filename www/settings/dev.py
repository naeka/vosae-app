# -*- coding:Utf-8 -*-
from mongoengine import connect
import djcelery

from settings.base import *


DEBUG = True
TASTYPIE_FULL_DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Used only in dev
SECRET_KEY = 'o4bpk#)!d5gxy7p9o5we6inz(yjqad=&o8p)n!3cr_k_csjl0i'

CACHES = {
    'default': {
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379:0",
        "OPTIONS": {
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
            'PARSER_CLASS': 'redis.connection.HiredisParser',
        }
    },
    'api_throttling': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'api-throttling'
    }
}

SITE_URL = "http://localhost:8000"
SITE_NAME = "Vosae Dev"

BROKER_URL = 'redis://localhost:6379/0'

CORS_ORIGIN_REGEX_WHITELIST = ('^https?://.*$',)


try:
    from settings.local import *
except ImportError:
    pass

connect(MONGO_DATABASE_NAME, tz_aware=True)
djcelery.setup_loader()

# Web endpoint must be defined
assert WEB_ENDPOINT, u'VOSAE_WEB_ENDPOINT is missing in environment'
