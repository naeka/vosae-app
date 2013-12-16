# -*- coding:Utf-8 -*-

from django.conf.urls import *
from django.utils.translation import ugettext_lazy as _
import views

urlpatterns = patterns(
    '',
    url(_(r'^account/signin/$'), views.signin, name="signin"),
    url(_(r'^account/signout/$'), views.signout, name="signout"),
    url(_(r'^account/signup/$'), views.signup, name="signup"),
    url(_(r'^account/activate/(?P<email>.+)/(?P<activation_key>\w+)/$'), views.activate, name='account_activate'),
    url(_(r'^account/identity/set/$'), views.set_identity, name='set_identity'),
    url(_(r'^account/password/set/$'), views.initial_password_setup, name='initial_password_setup'),
    url(_(r'^account/password/reset/$'), views.password_reset, {'template_name': 'account/password_reset_form.html', 'email_template_name': 'account/emails/password_reset_email.txt', 'html_email_template_name': 'account/emails/password_reset_email.html'}, name='password_reset'),
    url(_(r'^account/password/reset/done/$'), 'django.contrib.auth.views.password_reset_done', {'template_name': 'account/password_reset_done.html'}, name='password_reset_done'),
    url(_(r'^account/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$'), 'django.contrib.auth.views.password_reset_confirm', {'template_name': 'account/password_reset_confirm.html'}, name='password_reset_confirm'),
    url(_(r'^account/password/reset/complete/$'), 'django.contrib.auth.views.password_reset_complete', {'template_name': 'account/password_reset_complete.html'}, name='password_reset_complete'),
)
