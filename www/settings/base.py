# -*- coding:Utf-8 -*-

# Django settings for Vosae project.

import os
from django.core.urlresolvers import reverse_lazy


DEBUG = True
TRAVIS = False
TEMPLATE_DEBUG = DEBUG
# TASTYPIE_FULL_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

SITE_ROOT = os.path.dirname(os.path.realpath(__file__ + '/../'))
WEB_ENDPOINT = os.environ.get('VOSAE_WEB_ENDPOINT').rstrip('/') if os.environ.get('VOSAE_WEB_ENDPOINT') else None
SESSION_COOKIE_DOMAIN = os.environ.get('VOSAE_COOKIE_DOMAIN')
CSRF_COOKIE_DOMAIN = os.environ.get('VOSAE_COOKIE_DOMAIN')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'vosae.sqlite3',                      # Or path to database file if using sqlite3.
    }
}
MONGO_DATABASE_NAME = "vosae"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# If you set this to True, Django will use timezone-aware datetimes.
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

_ = lambda s: s
LANGUAGES = (
    ('en', _('English')),
    ('en-gb', _('British English')),
    ('fr', _('French')),
)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
LOCALE_PATHS = (
    os.path.join(SITE_ROOT, 'settings/locale'),
)

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(SITE_ROOT, 'static').replace('\\', '/')
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.VosaeLocaleMiddleware',
    'middleware.VosaeCorsMiddleware',
)

X_FRAME_OPTIONS = 'DENY'

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates'),
)

FONTS_DIR = os.path.join(SITE_ROOT, 'core/static/core/font')

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.formtools',
    'django.contrib.sitemaps',
    'djcelery',
    'tastypie_mongoengine',
    'django_gravatar',
    'storages',
    'gunicorn',
    'south',
    'corsheaders',
)

VOSAE_APPS = (
    'account',
    'core',
    'contacts',
    'docs',
    'invoicing',
    'organizer',
    'realtime',
    'notification',
    'timeline',
    'vosae_settings',
    'data_liberation',
)

INSTALLED_APPS += VOSAE_APPS

AUTHENTICATION_BACKENDS = (
    'account.backends.VosaeBackend',
)
AUTH_USER_MODEL = 'account.User'
LOGIN_URL = reverse_lazy('signin')
LOGOUT_URL = reverse_lazy('signout')
LOGIN_REDIRECT_URL = reverse_lazy('tenant_root')
LOGGED_IN_HOME = 'root'
ACCOUNT_SESSION_VALIDITY_HOURS = 1 * 24 * 30  # 30 days
ACCOUNT_ACTIVATION_DAYS = 2
ACCOUNT_ACTIVATED = 'ALREADY_ACTIVED'
ACCOUNT_ACTIVATION_REQUIRED = True

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'core.context_processors.vosae_settings',
    'core.context_processors.debug',
    'core.context_processors.travis',
    'core.context_processors.site'
)


# S3 Secret keys. If not in env, should be overriden in local.py settings.
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_DEFAULT_ACL = 'private'

AWS_QUERYSTRING_AUTH = False
DEFAULT_FILE_STORAGE = 'vosae_utils.VosaeS3BotoStorage'

FORMAT_MODULE_PATH = 'formats'

TEST_RUNNER = 'test_runner.VosaeTestRunner'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@vosae.com'

LOGIN_REDIRECT_URL = '/dashboard/'

# CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_REGEX_WHITELIST = ('^https://.*$', )
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ('GET', 'POST', 'PUT', 'DELETE', 'OPTIONS')
CORS_ALLOW_HEADERS = (
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-requested-with',
    'x-csrftoken',
    'x-tenant',
    'x-report-language',
    'x-wakeup'
)
CORS_EXPOSE_HEADERS = (
    'x-tenant',
    'x-report-language',
    'x-wakeup'
)

ES_SERVERS = [
    '127.0.0.1:9200'
]

ES_AUTH = None

ES_SETTINGS = {
    "analysis": {
        "filter": {
            "query_edgengram": {
                "type": "edgeNGram",
                "min_gram": 2,
                "max_gram": 30,
                "side": "front"
            },
            "reference_word_delimiter": {
                "type": "word_delimiter",
                "preserve_original": True
            }
        },
        "analyzer": {
            "query_index_analyzer": {
                "tokenizer": "whitespace",
                "filter": ["lowercase", "stop", "asciifolding", "reference_word_delimiter", "query_edgengram"]
            },
            "query_search_analyzer": {
                "tokenizer": "whitespace",
                "filter": ["lowercase", "stop", "asciifolding"]
            }
        }
    }
}

ES_ALL_CONFIG = {
    "enabled": True,
    "index_analyzer": "query_index_analyzer",
    "search_analyzer": "query_search_analyzer"
}


VOSAE_MODULES = (
    ('core', _('Core')),
    ('contacts', _('Contacts')),
    ('organizer', _('Organizer')),
    ('invoicing', _('Invoicing'))
)

OPEN_EXCHANGE_RATES_APP_ID = os.getenv('OPEN_EXCHANGE_RATES_APP_ID')
VOSAE_SUPPORTED_CURRENCIES = (
    ('AUD', _('Australian dollar')),
    ('BRL', _('Brazilian real')),
    ('CAD', _('Canadian dollar')),
    ('CHF', _('Swiss franc')),
    ('CNY', _('Chinese yuan')),
    ('DKK', _('Danish krone')),
    ('EGP', _('Egyptian pound')),
    ('EUR', _('Euro')),
    ('GBP', _('Pound sterling')),
    ('HKD', _('Hong Kong dollar')),
    ('INR', _('Indian rupee')),
    ('JPY', _('Japanese yen')),
    ('MAD', _('Moroccan dirham')),
    ('MXN', _('Mexican peso')),
    ('NOK', _('Norwegian krone')),
    ('NZD', _('New Zealand dollar')),
    ('RUB', _('Russian rouble')),
    ('SEK', _('Swedish krona')),
    ('TRY', _('Turkish lira')),
    ('USD', _('United States dollar'))
)

VOSAE_SUPPORTED_COUNTRIES = (
    ("BE", _('Belgium')),
    ("CH", _('Switzerland')),
    ("FR", _('France')),
    ("GB", _('Great Britain')),
    ("LU", _('Luxembourg')),
    ("US", _('United States')),
)

VOSAE_DOMAIN = 'vosae.com'
VOSAE_WWW_DOMAIN = 'www.' + VOSAE_DOMAIN


ORGANIZER_MAX_EVENT_OCCURRENCES = 730


GRAVATAR_DEFAULT_IMAGE = 'blank'

SENTRY_DSN = None

JOHNNY_MIDDLEWARE_KEY_PREFIX = 'jc_vosae'

# DO NOT PUT ANYTHING BELOW
