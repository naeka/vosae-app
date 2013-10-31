# -*- coding:Utf-8 -*-

from django.conf.urls import url, patterns


urlpatterns = patterns(
    'core.views',
    url(r'^file/(?P<tenant_slug>[-\w]+)/(?P<file_id>\w+)/d/$', 'download_file', name="download_file"),
    url(r'^file/(?P<tenant_slug>[-\w]+)/(?P<file_id>\w+)/s/$', 'download_file', {'stream': True}, name="stream_file"),
    url(r'^$', 'root', name="root"),
)
