# -*- coding:Utf-8 -*-

from django.contrib.auth import get_user_model

from tastypie.exceptions import ImmediateHttpResponse
from tastypie import http
from tastypie.authentication import SessionAuthentication, ApiKeyAuthentication

from core.models import VosaeUser


__all__ = (
    'VosaeSessionAuthentication',
    'VosaeApiKeyAuthentication'
)


class VosaeSessionAuthentication(SessionAuthentication):

    """
    Session-based authentication handler.  
    Used for webapp auth.
    """

    def is_authenticated(self, request, **kwargs):
        if hasattr(request, 'vosae_user') and not request.vosae_user.is_active():
            raise ImmediateHttpResponse(http.HttpUnauthorized())
        return super(VosaeSessionAuthentication, self).is_authenticated(request, **kwargs)

    def get_identifier(self, request):
        return request.user.email


class VosaeApiKeyAuthentication(ApiKeyAuthentication):

    """
    Handles API key auth, in which a user provides a email & API key.

    Uses the ``ApiKey`` model that ships with tastypie. If you wish to use
    a different model, override the ``get_key`` method to perform the key check
    as suits your needs.
    """

    def extract_credentials(self, request):
        if request.META.get('HTTP_AUTHORIZATION') and request.META['HTTP_AUTHORIZATION'].lower().startswith('apikey '):
            (auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()

            if auth_type.lower() != 'apikey':
                raise ValueError("Incorrect authorization header.")

            email, api_key = data.split(':', 1)
        else:
            email = request.GET.get('email') or request.POST.get('email')
            api_key = request.GET.get('api_key') or request.POST.get('api_key')

        return email, api_key

    def is_authenticated(self, request, **kwargs):
        """
        Finds the user and checks their API key.

        Should return either ``True`` if allowed, ``False`` if not or an
        ``HttpResponse`` if you need something custom.
        """
        UserModel = get_user_model()

        try:
            email, api_key = self.extract_credentials(request)
        except ValueError:
            return self._unauthorized()

        if not email or not api_key:
            return self._unauthorized()

        try:
            user = UserModel._default_manager.get(email=email)
        except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturned):
            return self._unauthorized()

        if not self.check_active(user):
            return False

        key_auth_check = self.get_key(user, api_key)
        if key_auth_check and not isinstance(key_auth_check, http.HttpUnauthorized):
            request.user = user
            if not getattr(request, 'vosae_user', None):
                if request.user.groups.filter(name=request.tenant.slug):
                    request.vosae_user = VosaeUser.objects.get(tenant=request.tenant, email=request.user.email)
                else:
                    raise ImmediateHttpResponse(http.HttpUnauthorized())
            if not request.vosae_user.is_active():
                raise ImmediateHttpResponse(http.HttpUnauthorized())

        return key_auth_check

    def get_key(self, user, api_key):
        """
        Attempts to find the API key for the user. Uses ``ApiKey`` by default
        but can be overridden.
        """
        from account.models import ApiKey

        try:
            ApiKey.objects.get(user=user, key=api_key)
        except ApiKey.DoesNotExist:
            return self._unauthorized()

        return True

    def get_identifier(self, request):
        """
        Provides a unique string identifier for the requestor.

        This implementation returns the user's email.
        """
        email, api_key = self.extract_credentials(request)
        return email or 'nouser'
