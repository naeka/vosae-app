# -*- coding:Utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import is_valid_path
from django.http import HttpResponseRedirect
from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.middleware.locale import LocaleMiddleware
from corsheaders.middleware import CorsMiddleware


__all__ = (
    'VosaeLocaleMiddleware',
)


class VosaeLocaleMiddleware(LocaleMiddleware):

    def process_response(self, request, response):
        language = translation.get_language()
        # Check if app has i18n_patterns urlconf
        is_i18n_pattern = hasattr(request, 'resolver_match') and getattr(request.resolver_match, 'app_name', None) in ('account',)
        # If path is '/', resolver_match is errored and not provided
        if request.path == '/' and request.user.is_anonymous():
            # On home, if not anonymous -> tenant_root
            is_i18n_pattern = True
        if (response.status_code == 404 and
                is_i18n_pattern
           and not translation.get_language_from_path(request.path_info)
           and self.is_language_prefix_patterns_used()):
            urlconf = getattr(request, 'urlconf', None)
            language_path = '/%s%s' % (language, request.path_info)
            path_valid = is_valid_path(language_path, urlconf)
            if (not path_valid and settings.APPEND_SLASH
                    and not language_path.endswith('/')):
                path_valid = is_valid_path("%s/" % language_path, urlconf)

            if path_valid:
                language_url = "%s://%s/%s%s" % (
                    request.is_secure() and 'https' or 'http',
                    request.get_host(), language, request.get_full_path())
                return HttpResponseRedirect(language_url)
        translation.deactivate()

        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = language
        return response


class VosaeCorsMiddleware(CorsMiddleware):

    """Middleware which adds headers for every API requests"""

    def process_request(self, request):
        if request.path.startswith('/api/'):
            return super(VosaeCorsMiddleware, self).process_request(request)
        return None

    def process_response(self, request, response):
        if request.path.startswith('/api/'):
            return super(VosaeCorsMiddleware, self).process_response(request, response)
        return response
