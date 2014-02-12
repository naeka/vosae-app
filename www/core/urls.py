# -*- coding:Utf-8 -*-

from django.conf.urls import url, patterns
from django.conf import settings


urlpatterns = patterns(
    'core.views',
    url(r'^file/(?P<tenant_slug>[-\w]+)/(?P<file_id>\w+)/d/$', 'download_file', name="download_file"),
    url(r'^file/(?P<tenant_slug>[-\w]+)/(?P<file_id>\w+)/s/$', 'download_file', {'stream': True}, name="stream_file"),
    url(r'^$', 'root', name="root"),
)

# if settings.DEBUG:
#     urlpatterns += patterns(
#         'core.views',
#         url(r'^403/$', 'error_403', name="error_403"),
#         url(r'^404/$', 'error_404', name="error_404"),
#         url(r'^500/$', 'error_500', name="error_500"),
#     )