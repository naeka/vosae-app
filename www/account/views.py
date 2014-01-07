# -*- coding:Utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _, get_language
import urllib2

from account.forms import SignupForm, SetIdentityForm
from account.decorators import login_forbidden

# Imports for Django 1.6 backported code
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import resolve_url
from django.contrib.auth.tokens import default_token_generator
from account.forms import PasswordResetForm


@login_forbidden
def signin(request):
    """Sign in using email with password."""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            request.session.set_expiry(settings.ACCOUNT_SESSION_VALIDITY_HOURS * 3600)

            # Stores the current language if different
            current_language = get_language()
            if request.user.browser_language != current_language:
                request.user.browser_language = current_language
                request.user.save(update_fields=['browser_language'])

            # Process redirect
            next = request.GET.get('next', False)
            if next:
                return HttpResponseRedirect(next)
            else:
                return redirect('root')
    else:
        form = AuthenticationForm()
    return render_to_response('account/signin.html', {'form': form}, context_instance=RequestContext(request))


@login_required
def signout(request):
    """Logout the request user"""
    logout(request)
    return redirect('root')


@login_forbidden
def signup(request):
    """Sign up using email with password."""
    if request.method == 'POST':
        form = SignupForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Thank you for your sign up on Vosae.\nPlease follow the instructions that we\'ve just sent to you by e-mail.'))
            return redirect('signin')
    else:
        form = SignupForm()
    return render_to_response('account/signup.html', {'form': form}, context_instance=RequestContext(request))


def activate(request, email, activation_key, template_name='account/activate_fail.html', extra_context=None):
    """Activate a user with an activation key."""
    UserModel = get_user_model()
    email = urllib2.unquote(email).decode('utf-8')
    user = UserModel.objects.activate_user(email, activation_key)
    if user:
        validate_email(email)
        auth_user = authenticate(email=user.email, check_password=False)
        login(request, auth_user)
    return redirect('root')


@login_required
def initial_password_setup(request):
    """
    Used by user to set his password when connecting the first time
    (when directly created through VosaeUser pre_save hook)
    """
    if request.user.has_usable_password():
        return redirect('root')

    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('root'))
    else:
        form = SetPasswordForm(None)
    context = {
        'form': form,
    }
    return TemplateResponse(request, 'account/initial_password_setup.html', context)


@login_required
def set_identity(request):
    """Used by user to set his identity (first_name/last_name)"""
    if request.user.has_identity_set():
        return redirect('root')

    if request.method == 'POST':
        form = SetIdentityForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('root'))
    else:
        form = SetIdentityForm(None)
    context = {
        'form': form,
    }
    return TemplateResponse(request, 'account/set_identity.html', context)


@csrf_protect
def password_reset(request, is_admin_site=False,
                   template_name='registration/password_reset_form.html',
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None,
                   html_email_template_name=None):
    """
    Backported from django 1.6 for `html_email_template_name`
    To be removed as soon as we upgrade to 1.6
    """
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
        'title': _('Password reset'),
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)