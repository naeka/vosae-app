# -*- coding:Utf-8 -*-

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, loader
from django.views.generic import TemplateView
from django.utils.formats import get_format
from django.conf import settings

from django.http import (
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseServerError,
    Http404
)
import urllib2

from core.models import (
    Tenant,
    VosaeUser,
    VosaeFile
)


def error_403(request):
    t = loader.get_template('core/errors/403.html')
    return HttpResponseForbidden(t.render(RequestContext(request)))


def error_404(request):
    t = loader.get_template('core/errors/404.html')
    return HttpResponseNotFound(t.render(RequestContext(request)))


def error_500(request):
    t = loader.get_template('core/errors/500.html')
    return HttpResponseServerError(t.render(RequestContext(request)))


def root(request):
    if not request.user.is_authenticated():
        return redirect('signin')
    return HttpResponseRedirect(settings.WEB_ENDPOINT)


def download_file(request, tenant_slug, file_id, public_token=None, stream=False):
    try:
        request.tenant = Tenant.objects.get(slug=tenant_slug)
        if not request.user.is_anonymous():
            request.user.groups.get(name=tenant_slug)
            request.vosae_user = VosaeUser.objects.get(tenant=request.tenant, email=request.user.email)
        else:
            # If anonymous user, public_token is required
            assert public_token is not None
    except:
        raise Http404()

    if request.vosae_user and not request.vosae_user.has_perm("see_vosaefile"):
        return HttpResponseForbidden()

    try:
        kwargs = {'tenant': request.tenant, 'id': file_id}
        if public_token:
            kwargs.update(public_token=public_token)

        vosae_file = VosaeFile.objects.get(**kwargs)

        if not public_token:
            # Since public token is provided, file is assumed as publicly accessible
            # and authorization checks are useless.
            for perm in vosae_file.permissions:
                if not request.vosae_user.has_perm(perm):
                    return HttpResponseForbidden()
        response_headers = {'response-content-disposition': 'inline; filename="{0}"'.format(str(urllib2.quote(vosae_file.name.encode('utf8'))))}
        s3url = vosae_file.file.key.generate_url(20, response_headers=response_headers if stream else None)
        return HttpResponseRedirect(s3url)
    except:
        raise Http404()


def spec(request):
    # During specs tests we use local static files (even during Travis builds)
    original_settings_staticfiles_storage = settings.STATICFILES_STORAGE

    settings.STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

    # Force the auth user email during specs
    request.user.email = "spec@vosae.com"

    formats = {
        # Defaults
        "DECIMAL_SEPARATOR": get_format("DECIMAL_SEPARATOR"),
        "THOUSAND_SEPARATOR": get_format("THOUSAND_SEPARATOR"),
        "NUMBER_GROUPING": get_format("NUMBER_GROUPING"),

        # Custom
        "MON_DECIMAL_POINT": get_format("MON_DECIMAL_POINT"),
        "MON_THOUSANDS_SEP": get_format("MON_THOUSANDS_SEP"),
        "N_CS_PRECEDES": get_format("N_CS_PRECEDES"),
        "P_CS_PRECEDES": get_format("P_CS_PRECEDES"),
        "N_SEP_BY_SPACE": get_format("N_SEP_BY_SPACE"),
        "P_SEP_BY_SPACE": get_format("P_SEP_BY_SPACE"),
        "N_SIGN_POSN": get_format("N_SIGN_POSN"),
        "P_SIGN_POSN": get_format("P_SIGN_POSN"),
        "NEGATIVE_SIGN": get_format("NEGATIVE_SIGN"),
        "POSITIVE_SIGN": get_format("POSITIVE_SIGN"),
    }

    response = render_to_response("core/spec.html", {'formats': formats}, context_instance=RequestContext(request))
    settings.STATICFILES_STORAGE = original_settings_staticfiles_storage
    return response


class TextTemplateView(TemplateView):

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'text/plain'
        return super(TemplateView, self).render_to_response(context, **response_kwargs)
