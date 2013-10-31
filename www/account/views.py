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
