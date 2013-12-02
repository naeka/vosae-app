# -*- coding:Utf-8 -*-

from django.conf import settings
from django.http import HttpResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.cache import patch_cache_control, patch_vary_headers
from django.views.decorators.csrf import csrf_exempt
import mongoengine

from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie import http, fields as tastypie_fields
from tastypie.authentication import MultiAuthentication
from tastypie_mongoengine import resources, paginator

from core.api.utils.authentication import VosaeSessionAuthentication, VosaeApiKeyAuthentication
from core.api.utils.authorization import VosaeUserAuthorization
from core.api.utils.serializers import VosaeSerializer
from core.api.utils.http import VosaeHttpTooManyRequests
from core.api.utils.throttling import VosaeCacheDBThrottle
from core.api.utils.mixins import TenantRequiredMixinResource
from core.api.utils.metaclass import VosaeModelDeclarativeMetaclass
from core.api import signals


__all__ = (
    'VosaeResource',
    'TenantResource'
)


class VosaeResource(resources.MongoEngineResource):

    """
    Resource for defining embedded documents or not per-tenant documents
    (eg. Calendar, Currency, etc.)
    """
    __metaclass__ = VosaeModelDeclarativeMetaclass

    class Meta:
        list_allowed_methods = ('get', 'post')
        detail_allowed_methods = ('get', 'put', 'delete')
        authentication = MultiAuthentication(VosaeSessionAuthentication(), VosaeApiKeyAuthentication())
        authorization = VosaeUserAuthorization()
        serializer = VosaeSerializer()
        paginator_class = paginator.Paginator
        always_return_data = True
        throttle = VosaeCacheDBThrottle(throttle_at=4000, timeframe=3600)
        max_limit = 100

    def wrap_view(self, view):
        """
        Wraps methods so they can be called in a more functional way as well
        as handling exceptions better.

        Note that if ``BadRequest`` or an exception with a ``response`` attr
        are seen, there is special handling to either present a message back
        to the user or return the response traveling with the exception.
        """
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                self.handle_tenant_access(request)  # Override
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                # Our response can vary based on a number of factors, use
                # the cache class to determine what we should ``Vary`` on so
                # caches won't return the wrong (cached) version.
                varies = getattr(self._meta.cache, "varies", [])

                if varies:
                    patch_vary_headers(response, varies)

                if self._meta.cache.cacheable(request, response):
                    if self._meta.cache.cache_control():
                        # If the request is cacheable and we have a
                        # ``Cache-Control`` available then patch the header.
                        patch_cache_control(response, **self._meta.cache.cache_control())

                if request.is_ajax() and not response.has_header("Cache-Control"):
                    # IE excessively caches XMLHttpRequests, so we're disabling
                    # the browser cache here.
                    # See http://www.enhanceie.com/ie/bugs.asp for details.
                    patch_cache_control(response, no_cache=True)

                return response
            except (BadRequest, tastypie_fields.ApiFieldError) as e:
                data = {"error": e.args[0] if getattr(e, 'args') else ''}
                return self.error_response(request, data, response_class=http.HttpBadRequest)
            except ValidationError as e:
                data = {"error": e.messages}
                return self.error_response(request, data, response_class=http.HttpBadRequest)
            except Exception as e:
                if hasattr(e, 'response'):
                    return e.response

                # A real, non-expected exception.
                # Handle the case where the full traceback is more helpful
                # than the serialized error.
                if settings.DEBUG and getattr(settings, 'TASTYPIE_FULL_DEBUG', False):
                    raise

                # Re-raise the error to get a proper traceback when the error
                # happend during a test case
                if request.META.get('SERVER_NAME') == 'testserver':
                    raise

                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)

        return wrapper

    def handle_tenant_access(self, request):
        pass

    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """Adds the `X-RateLimit-*` headers to the response"""
        response = super(VosaeResource, self).create_response(request, data, response_class, **response_kwargs)
        throttle_stats = getattr(request, 'throttle_stats', None)
        if throttle_stats:
            response['X-RateLimit-Remaining'] = throttle_stats.get('remaining') - 1
            response['X-RateLimit-Limit'] = throttle_stats.get('limit')
        return response

    def throttle_check(self, request):
        """
        Handles checking if the user should be throttled.

        Mostly a hook, this uses class assigned to ``throttle`` from
        ``Resource._meta``.

        Backported from tastypie
        """
        identifier = self._meta.authentication.get_identifier(request)

        # Check to see if they should be throttled.
        request.throttle_stats = self._meta.throttle.should_be_throttled(identifier)
        if request.throttle_stats.get('remaining') <= 0:
            # Throttle limit exceeded.
            raise ImmediateHttpResponse(response=VosaeHttpTooManyRequests(throttle_stats=request.throttle_stats))

    def build_schema(self):
        data = super(VosaeResource, self).build_schema()
        data.update({
            'resource_name': self._meta.resource_name,
            'detail_specific_methods': getattr(self._meta, 'detail_specific_methods', ())
        })
        return data

    def save(self, bundle, skip_errors=False):
        """
        Mix of tastypie and tastypie_mongoengine
        M2M are processed before main save
        """
        signals.pre_save.send(self.__class__, resource=self, bundle=bundle)

        self.is_valid(bundle)

        if bundle.errors and not skip_errors:
            raise ImmediateHttpResponse(response=self.error_response(bundle.request, bundle.errors))

        # Check if they're authorized.
        if bundle.obj.pk:
            created = False
            self.authorized_update_detail(self.get_object_list(bundle.request), bundle)
        else:
            created = True
            self.authorized_create_detail(self.get_object_list(bundle.request), bundle)

        signals.pre_save_post_validation.send(self.__class__, resource=self, bundle=bundle)

        try:
            # Save FKs just in case.
            self.save_related(bundle)

            # Now pick up the M2M bits.
            m2m_bundle = self.hydrate_m2m(bundle)
            self.save_m2m(m2m_bundle)

            # Save the main object.
            bundle.obj.save()
            bundle.objects_saved.add(self.create_identifier(bundle.obj))
        except mongoengine.ValidationError as e:
            raise ValidationError(e.message)

        signals.post_save.send(self.__class__, resource=self, bundle=bundle, created=created)
        return bundle

    def save_related(self, bundle):
        """
        Same of tastypie but without the part saving the related resource.
        In our case, done by the main save()
        """
        for field_name, field_object in self.fields.items():
            if not getattr(field_object, 'is_related', False):
                continue

            if getattr(field_object, 'is_m2m', False):
                continue

            if not field_object.attribute:
                continue

            if field_object.readonly:
                continue

            if field_object.blank and field_name not in bundle.data:
                continue

            # Get the object.
            try:
                related_obj = getattr(bundle.obj, field_object.attribute)
            except ObjectDoesNotExist:
                related_obj = bundle.related_objects_to_save.get(field_object.attribute, None)

            # Because sometimes it's ``None`` & that's OK.
            if related_obj:
                if field_object.related_name:
                    if not self.get_bundle_detail_data(bundle):
                        bundle.obj.save()

                    setattr(related_obj, field_object.related_name, bundle.obj)

                # Before we build the bundle & try saving it, let's make sure we
                # haven't already saved it.
                obj_id = self.create_identifier(related_obj)

                if obj_id in bundle.objects_saved:
                    # It's already been saved. We're done here.
                    continue

                setattr(bundle.obj, field_object.attribute, related_obj)

    def save_m2m(self, bundle):
        """
        Same of tastypie_mongoengine but without the part saving the related resources.
        In our case, done by the main save()
        """
        for field_name, field_object in self.fields.items():
            if not getattr(field_object, 'is_m2m', False):
                continue

            if not field_object.attribute:
                continue

            if field_object.readonly:
                continue

            related_objs = []

            for related_bundle in bundle.data[field_name]:
                related_objs.append(related_bundle.obj)

            setattr(bundle.obj, field_object.attribute, related_objs)

    def obj_create(self, bundle, **kwargs):
        signals.pre_create.send(self.__class__, resource=self, bundle=bundle)
        bundle = super(VosaeResource, self).obj_create(bundle, **kwargs)
        signals.post_create.send(self.__class__, resource=self, bundle=bundle)
        return bundle

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        signals.pre_update.send(self.__class__, resource=self, bundle=bundle)
        bundle = super(VosaeResource, self).obj_update(bundle, skip_errors, **kwargs)
        signals.post_update.send(self.__class__, resource=self, bundle=bundle)
        return bundle

    def obj_delete(self, bundle, **kwargs):
        signals.pre_delete.send(self.__class__, resource=self, bundle=bundle)
        super(VosaeResource, self).obj_delete(bundle, **kwargs)
        signals.post_delete.send(self.__class__, resource=self, bundle=bundle)

    def log_throttled_access(self, request):
        super(VosaeResource, self).log_throttled_access(request)
        signals.resource_access.send(self.__class__, resource=self, request=request)


class TenantResource(TenantRequiredMixinResource, VosaeResource):

    """
    Resource for defining per-tenant documents
    """

    def get_object_list(self, request):
        """Filters queryset based on the tenant"""
        object_list = super(TenantResource, self).get_object_list(request)
        if request and getattr(request, 'tenant', None):
            return object_list.filter(tenant=request.tenant)
        return object_list

    def hydrate(self, bundle):
        """Automatically set tenant to resource object"""
        bundle = super(TenantResource, self).hydrate(bundle)
        bundle.obj.tenant = bundle.request.tenant
        return bundle
