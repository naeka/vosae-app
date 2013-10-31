# -*- coding:Utf-8 -*-

from django.db import IntegrityError
from django.http import HttpResponse
from django import forms
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.validation import FormValidation
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie.authentication import MultiAuthentication

from core.api.utils import (
    TenantRequiredMixinResource,
    VosaeSessionAuthentication,
    VosaeApiKeyAuthentication,
    VosaeUserAuthorization,
    VosaeCacheDBThrottle
)
from account.models import ApiKey
from account.api.doc import HELP_TEXT


__all__ = (
    'ApiKeyResource',
)


class ApiKeyForm(forms.Form):

    """ApiKey form used for field validation"""
    label = forms.CharField(max_length=256)


class ApiKeyResource(ModelResource, TenantRequiredMixinResource):
    label = fields.CharField(
        attribute='label',
        help_text=HELP_TEXT['api_key']['label']
    )
    created_at = fields.DateTimeField(
        attribute='created_at',
        readonly=True,
        help_text=HELP_TEXT['api_key']['created_at']
    )

    class Meta:
        resource_name = 'api_key'
        queryset = ApiKey.objects.all()
        list_allowed_methods = ('get', 'post', 'delete')
        detail_allowed_methods = ('get', 'delete')
        fields = ('id', 'label', 'created_at')

        authentication = MultiAuthentication(VosaeSessionAuthentication(), VosaeApiKeyAuthentication())
        authorization = VosaeUserAuthorization()
        always_return_data = True
        validation = FormValidation(form_class=ApiKeyForm)
        throttle = VosaeCacheDBThrottle(throttle_at=4000, timeframe=3600)
        max_limit = 100

    def dispatch(self, request_type, request, **kwargs):
        self.handle_tenant_access(request)  # Done here, simpler than in wrap_views's wrapper
        return super(ApiKeyResource, self).dispatch(request_type, request, **kwargs)

    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """Adds the `X-RateLimit-*` headers to the response"""
        response = super(ApiKeyResource, self).create_response(request, data, response_class, **response_kwargs)
        throttle_stats = getattr(request, 'throttle_stats', None)
        if throttle_stats:
            response['X-RateLimit-Remaining'] = throttle_stats.get('remaining') - 1
            response['X-RateLimit-Limit'] = throttle_stats.get('limit')
        return response

    def throttle_check(self, request):
        from core.api.utils import VosaeHttpTooManyRequests
        identifier = self._meta.authentication.get_identifier(request)
        # Check to see if they should be throttled.
        request.throttle_stats = self._meta.throttle.should_be_throttled(identifier)
        if request.throttle_stats.get('remaining') <= 0:
            # Throttle limit exceeded.
            raise ImmediateHttpResponse(response=VosaeHttpTooManyRequests(throttle_stats=request.throttle_stats))

    def get_object_list(self, request):
        object_list = super(ApiKeyResource, self).get_object_list(request)
        return object_list.filter(user=request.user)

    def obj_create(self, bundle, **kwargs):
        try:
            return super(ApiKeyResource, self).obj_create(bundle, **kwargs)
        except IntegrityError:
            raise BadRequest("Api key label must be unique")

    def hydrate(self, bundle):
        bundle = super(ApiKeyResource, self).hydrate(bundle)
        bundle.obj.user = bundle.request.user
        return bundle

    def dehydrate(self, bundle):
        bundle = super(ApiKeyResource, self).dehydrate(bundle)
        if bundle.request.method.lower() == 'post':
            bundle.data.update(key=bundle.obj.key)
        return bundle
