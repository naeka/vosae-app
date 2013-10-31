# -*- coding:Utf-8 -*-

from django.conf.urls import url, patterns
import views

urlpatterns = patterns(
    '',
    url("^rt/auth/$", views.pusher_auth, name="pusher_auth"),
)
