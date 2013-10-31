# -*- coding:Utf-8 -*-

from django.conf.urls import url

from tastypie import fields as base_fields
from tastypie.utils import trailing_slash
from tastypie_mongoengine import fields

from core.api.utils import VosaeResource, TenantResource
from vosae_settings.models import TenantSettings


__all__ = (
    'TenantSettingsResource',
)


class TenantSettingsResource(TenantResource):
    core = fields.EmbeddedDocumentField(
        embedded='vosae_settings.api.resources.core_settings.CoreSettingsResource',
        attribute='core',
        null=True,  # XXX: Temp, because core settings are currently empty
        blank=True,  # XXX: Temp, because core settings are currently empty
    )
    invoicing = fields.EmbeddedDocumentField(
        embedded='vosae_settings.api.resources.invoicing_settings.InvoicingSettingsResource',
        attribute='invoicing',
    )

    class Meta(TenantResource.Meta):
        resource_name = 'tenant_settings'
        queryset = TenantSettings.objects.all()
        excludes = ('tenant', 'id')
        list_allowed_methods = ()
        detail_allowed_methods = ('get', 'put')
        include_resource_uri = False

    def base_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
        ]

    def dispatch_list(self, request, **kwargs):
        kwargs.update(pk=unicode(request.tenant.tenant_settings.id))
        return self.dispatch('detail', request, **kwargs)

    def dispatch(self, request_type, request, **kwargs):
        # Ancestor + 1 dispatch
        return super(VosaeResource, self).dispatch(request_type, request, **kwargs)
