# -*- coding:Utf-8 -*-

from django.conf.urls import url, patterns

from docs import views


urlpatterns = patterns('',
    url(r'^docs/api/$', views.doc_home, name="doc_home"),
    url(r'^docs/api/(?P<app>[-\w]+)/(?P<resource>[-\w]+)$', views.doc_resource, name='doc_resource'),
)
