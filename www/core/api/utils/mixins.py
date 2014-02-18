# -*- coding:Utf-8 -*-

from django.http import HttpResponse
from django.conf.urls import url
from django.utils.http import urlquote
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.clickjacking import xframe_options_sameorigin
from mongoengine import NotUniqueError

from tastypie.exceptions import ImmediateHttpResponse
from tastypie.utils import trailing_slash
from tastypie.exceptions import BadRequest
from tastypie import http, fields as base_fields
from tastypie_mongoengine.resources import MongoEngineResource

import mimetypes

from core.models import Tenant, VosaeUser
from core.api.utils.exceptions import TenantNotProvided, RestorablePostConflict
from core.api.utils.metaclass import VosaeModelDeclarativeMetaclass
from core.api.doc import HELP_TEXT


__all__ = (
    'TenantRequiredMixinResource',
    'TenantRequiredOnPutMixinResource',
    'MultipartMixinResource',
    'VosaeIMEXMixinResource',
    'RestorableMixinResource',
    'RemoveFilesOnReplaceMixinResource'
)


def generic_tenant_access(request):
    try:
        tenant_slug = request.META.get('HTTP_X_TENANT', request.GET.get('x_tenant', None))
        if not tenant_slug:
            raise TenantNotProvided()
        request.tenant = Tenant.objects.get(slug=tenant_slug)
        if not request.user.is_anonymous():
            # API used with BasicAuth or SessionAuth: set VosaeUser.
            if request.user.groups.get(name=tenant_slug):
                request.vosae_user = VosaeUser.objects.get(tenant=request.tenant, email=request.user.email)
    except TenantNotProvided as e:
        raise e
    except:
        raise ImmediateHttpResponse(http.HttpUnauthorized())


class TenantRequiredMixinResource(object):

    def handle_tenant_access(self, request):
        return generic_tenant_access(request)


class TenantRequiredOnPutMixinResource(object):

    def handle_tenant_access(self, request):
        if request.method.lower() in ['put']:
            return generic_tenant_access(request)


class MultipartMixinResource(object):

    """Mixin used to handle binary uploads through tastypie"""

    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')

        if format == 'application/x-www-form-urlencoded':
            return request.POST

        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)

            return data

        return super(MultipartMixinResource, self).deserialize(request, data, format)

    def put_detail(self, request, **kwargs):
        if request.META.get('CONTENT_TYPE').startswith('multipart') and not hasattr(request, '_body'):
            request._body = ''

        return super(MultipartMixinResource, self).put_detail(request, **kwargs)


class VosaeIMEXMixinResource(object):

    """Mixin for import/export operations"""

    def get_serializer(self, slug_or_mimetype):
        for serializer in self._meta.available_imex_serializers:
            if serializer.type_slug == slug_or_mimetype:
                return serializer
        for serializer in self._meta.available_imex_serializers:
            for mime in serializer.type_mime:
                if mime == slug_or_mimetype:
                    return serializer
        raise Exception('Serializer not available')

    def prepend_urls(self):
        """Add urls for resources import/export."""
        urls = []
        if self._meta.available_imex_serializers:
            imex_serializers = '|'.join([s.type_slug for s in self._meta.available_imex_serializers])
            urls.extend((
                url(r'^(?P<resource_name>%s)/import%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('import_entries'), name='api_import_entries'),
                url(r'^(?P<resource_name>%s)/export/(?P<serializer_slug>(%s))%s$' % (self._meta.resource_name, imex_serializers, trailing_slash()), self.wrap_view('export_entries'), name='api_export_entries'),
                url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/export/(?P<serializer_slug>(%s))%s$' % (self._meta.resource_name, imex_serializers, trailing_slash()), self.wrap_view('export_entry'), name='api_export_entry'),
            ))
        return urls

    def import_entries(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)

        try:
            uploaded_file = request.FILES['uploaded_file']
            content_type = getattr(uploaded_file, 'content_type', mimetypes.guess_type(uploaded_file.name)[0])
            serializer = self.get_serializer(content_type)()
            if not hasattr(serializer, 'deserialize'):
                raise
            import_result = self.do_import(request, serializer, import_buffer=uploaded_file.read())
        except:
            raise BadRequest('Import is not available')

        self.log_throttled_access(request)
        bundles = [self.build_bundle(obj=obj, request=request) for obj in import_result.success]
        to_be_serialized = {}
        to_be_serialized['success'] = [self.get_resource_uri(bundle) for bundle in bundles]
        to_be_serialized['errors'] = import_result.errors
        to_be_serialized['meta'] = import_result.meta
        return self.create_response(request, to_be_serialized)

    def do_import(self, request, serializer, import_buffer):
        raise NotImplementedError("VosaeIMEXMixinResource's derivatives must implement do_import() method")

    @xframe_options_sameorigin
    def export_entries(self, request, serializer_slug, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        try:
            serializer = self.get_serializer(serializer_slug)()
            if not hasattr(serializer, 'serialize'):
                raise
            export_objects = self.get_object_list(request)
            if not export_objects:
                return http.HttpNotFound()
            exported_buffer, filename = self.do_export(request, serializer, export_objects=export_objects)
            if isinstance(exported_buffer, HttpResponse):
                return exported_buffer
        except Exception as e:
            raise BadRequest('Can\'t export. %s' % e)

        self.log_throttled_access(request)

        response = HttpResponse(exported_buffer, content_type=serializer.type_mime[0])
        response['Content-Disposition'] = 'attachment; filename="%s"' % urlquote('.'.join([filename, serializer.type_ext]))
        return response

    @xframe_options_sameorigin
    def export_entry(self, request, serializer_slug, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        try:
            bundle = self.build_bundle(request=request)
            obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()

        try:
            serializer = self.get_serializer(serializer_slug)()
            export_objects = [obj]
            exported_buffer, filename = self.do_export(request, serializer, export_objects=export_objects)
            if isinstance(exported_buffer, HttpResponse):
                return exported_buffer
        except Exception as e:
            raise BadRequest('Can\'t export. %s' % e)

        self.log_throttled_access(request)

        response = HttpResponse(exported_buffer, content_type=serializer.type_mime[0])
        response['Content-Disposition'] = 'attachment; filename="%s"' % urlquote('.'.join([filename, serializer.type_ext]))
        return response

    def do_export(self, request, serializer, export_objects):
        raise NotImplementedError("Can't export directly. Needs subclassing.")


class RestorableMixinResource(MongoEngineResource):

    """
    Restorable resources can not be deleted. A special state flag is set.  
    Restorable can still be accessed, but only on a detail request.
    """
    __metaclass__ = VosaeModelDeclarativeMetaclass

    state = base_fields.CharField(
        attribute='state',
        use_in='detail',
        readonly=True,
        help_text=HELP_TEXT['restorable_mixin']['state']
    )

    def is_restorable(self):
        """By default, always restorable"""
        return True

    def get_object_list(self, request):
        """Only display non-DELETED elements when getting list"""
        if request.method.lower() == 'get' and request.resolver_match.url_name == 'api_dispatch_list':
            return super(RestorableMixinResource, self).get_object_list(request).filter(state__ne=self._meta.object_class.DELETE_STATE)
        return super(RestorableMixinResource, self).get_object_list(request)

    def obj_create(self, bundle, **kwargs):
        try:
            return super(RestorableMixinResource, self).obj_create(bundle, **kwargs)
        except NotUniqueError:
            unique_fields = [field_name for field_name, field in self._meta.object_class._fields.iteritems() if field.unique]

            # If the header is set, try to restore the document
            # Moving to the update process
            if self.is_restorable() and bundle.request.META.get('HTTP_X_RESTORE'):
                filter_kwargs = {}
                for field in unique_fields:
                    filter_kwargs[field] = bundle.data.get(field)
                bundle.obj = self.get_object_list(bundle.request).filter(**filter_kwargs)[0]
                bundle.obj.state = bundle.request.META.get('HTTP_X_RESTORE')
                return self.obj_update(bundle, **kwargs)

            # If the header is not set, raise an explicative error message
            if len(unique_fields) == 1:
                err_msg = 'A document with this {0} already exists. It can be restored thanks to the X-Restore header (if in a DELETED/INACTIVE state)  or you can set different values'.format(*unique_fields)
            else:
                err_msg = 'A document with these {0} already exists. It can be restored thanks to the X-Restore header (if in a DELETED/INACTIVE state)  or you can set different values'.format(', '.join(unique_fields))
            raise RestorablePostConflict(http.HttpConflict(err_msg))

    def authorized_update_detail(self, object_list, bundle):
        if bundle.obj and bundle.obj.state == bundle.obj.DELETE_STATE:
            raise BadRequest('A deleted document can\'t be updated')


class RemoveFilesOnReplaceMixinResource(object):

    """Mixin used to ensure that a replaced file is well deleted from its backend"""
    TO_REMOVE_ON_REPLACE = []

    def __new__(cls, *args, **kwargs):
        instance = super(RemoveFilesOnReplaceMixinResource, cls).__new__(cls)
        for field in instance.TO_REMOVE_ON_REPLACE:
            setattr(instance, 'hydrate_{0}'.format(field), gen_filefield_hydrate(cls, field))
        return instance

    def obj_update(self, bundle, **kwargs):
        created = super(RemoveFilesOnReplaceMixinResource, self).obj_update(bundle, **kwargs)
        if hasattr(bundle, 'previous_files'):
            for field in self.TO_REMOVE_ON_REPLACE:
                if field in bundle.previous_files and getattr(bundle.obj, field) != bundle.previous_files[field]:
                    bundle.previous_files[field].delete()
        return created


def gen_filefield_hydrate(cls, field):
    def hydrate_filefield(bundle):
        if hasattr(super(cls, cls), 'hydrate_{0}'.format(field)):
            bundle = getattr(super(cls, cls), 'hydrate_{0}'.format(field))(cls, bundle)
        if getattr(bundle.obj, field):
            if not hasattr(bundle, 'previous_files'):
                bundle.previous_files = dict()
            bundle.previous_files[field] = getattr(bundle.obj, field)
        return bundle
    return hydrate_filefield
