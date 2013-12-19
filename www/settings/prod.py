# -*- coding:Utf-8 -*-
import os
from mongoengine import connect
import djcelery
import urlparse

from settings.base import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG

# The secret key is different on every env for maximum security
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# Emails can be only send from @vosae in production for security purpose
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# If we use Mandrill in production we need the mandrill api key
MANDRILL_API_KEY = os.getenv('MANDRILL_APIKEY')

# DATABASE CONFIGURATION SHOULD BE DEFINED HERE:
# MYSQL EXAMPLE:

# MYSQL DATABASE
# mysql_url = urlparse.urlparse(os.getenv('MYSQL_DATABASE_URL'))
# DATABASES['default'] = {
#     'ENGINE': 'django.db.backends.mysql',
#     'HOST': mysql_url.hostname,
#     'USER': mysql_url.username,
#     'NAME': mysql_url.path[1:],
#     'PASSWORD': mysql_url.password,
#     'OPTIONS': {
#         'ssl': {
#             'ca': SITE_ROOT + '/../cert/vosae/mysql_ca.pem',
#             'cert': SITE_ROOT + '/../cert/vosae/mysql_cert.pem',
#             'key': SITE_ROOT + '/../cert/vosae/mysql_id-key-no-password.pem'
#         },
#     }
# }


# Set your DSN value
SENTRY_DSN = os.getenv('SENTRY_DSN')

# Add raven to the list of installed apps
INSTALLED_APPS += (
    # ...
    'raven.contrib.django',
)

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'johnny.middleware.LocalStoreClearMiddleware',
    'johnny.middleware.QueryCacheMiddleware',
) + MIDDLEWARE_CLASSES


# Allowed hosts must be defined
ALLOWED_HOSTS = ("app.vosae.example.com",)


SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Caches must be defined
CACHES = {
    'default': {
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379:0",
        "OPTIONS": {
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
            'PARSER_CLASS': 'redis.connection.HiredisParser',
        }
    },
    'johnny': {
        'BACKEND': 'vosae_utils.JohnnyPyLibMCCache',
        'LOCATION': os.environ.get('MEMCACHE_SERVERS', '').replace(',', ';'),
        'JOHNNY_CACHE': True,
        'BINARY': True,
    },
    'api_throttling': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'LOCATION': os.environ.get('MEMCACHE_SERVERS', '').replace(',', ';'),
        'PREFIX': 'api_throttling',
        'TIMEOUT': 3600,
        'BINARY': True,
    },
    'staticfiles': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'staticfiles',
        'TIMEOUT': 60 * 60 * 24 * 365,
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# Static configuation
AWS_STATIC_BUCKET_NAME = ''  # Must be defined
STATIC_URL = os.environ['STATIC_URL']
AWS_S3_CUSTOM_DOMAIN = os.environ['STATIC_URL_DOMAIN']
STATICFILES_STORAGE = 'vosae_utils.S3CachedStorage'


# Site information
SITE_URL = "https://app.vosae.com"
SITE_NAME = "Vosae"


# Celery broker
BROKER_URL = os.getenv('BROKER_URL')
CELERY_IGNORE_RESULT = True
CELERY_DISABLE_RATE_LIMITS = True


# Elasticsearch
es_url = urlparse.urlparse(os.getenv('ES_URL'))
ES_SERVERS = [
    (es_url.scheme, es_url.hostname, es_url.port or '80')
]

ES_AUTH = {
    "username": es_url.username,
    "password": es_url.password
}

# PUSHER
PUSHER_URL = urlparse.urlparse(os.getenv('PUSHER_URL'))
PUSHER_APP_ID = PUSHER_URL.path.split('/')[-1]
PUSHER_KEY = PUSHER_URL.username
PUSHER_SECRET = PUSHER_URL.password
PUSHER_HOST = PUSHER_URL.hostname


# Import host conf here if needed
# try:
#     from .heroku import *
# except:
#     pass


# Web endpoint must be defined
assert WEB_ENDPOINT, u'VOSAE_WEB_ENDPOINT is missing in environment'

connect(MONGO_DATABASE_NAME, host=os.getenv('MONGODB_URL'), tz_aware=True)
djcelery.setup_loader()
