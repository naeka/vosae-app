# -*- coding:Utf-8 -*-

from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.i18n import i18n_patterns
from core.views import TextTemplateView
from django.conf.urls import patterns, url, include


from django.contrib import admin
from djrill import DjrillAdminSite
admin.site = DjrillAdminSite()
admin.autodiscover()

from api import v1_api
from docs.views import StaticSitemap, DocsSitemap


handler403 = 'core.views.error_403'
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'

sitemaps = dict(
    static=StaticSitemap,
    docs=DocsSitemap,
)

languages = '|'.join([l[0] for l in settings.LANGUAGES])

# part of the app with language suffix (ie /en/signin)
i18n_urlpatterns = i18n_patterns(
    '',
    (r'', include('account.urls', app_name='account')),
)

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    (r'^api/', include(v1_api.urls)),
)

# If debug get static files: must be here or with the realtime server (in dev) we can' get static files
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns(
    '',
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps, 'template_name': 'core/sitemap.xml'}),
    url(r'^robots\.txt$', TextTemplateView.as_view(template_name="core/robots.txt")),
)

urlpatterns += i18n_urlpatterns

urlpatterns += patterns(
    '',
    (r'', include('core.urls')),
    (r'', include('docs.urls')),
    (r'', include('realtime.urls')),
)
