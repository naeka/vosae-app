# -*- coding:Utf-8 -*-

from django.contrib.auth.models import Group

from tastypie import fields as base_fields, exceptions as tastypie_exceptions
from tastypie.utils import dict_strip_unicode_keys
from tastypie_mongoengine import fields
from vosae_settings.fields import SupportedCurrenciesListField
from core.api.utils import (
    VosaeResource,
    VosaeGenericAuthorization,
    TenantRequiredOnPutMixinResource,
    RemoveFilesOnReplaceMixinResource
)
from core.models import Tenant, VosaeUser
from core.tasks import fill_tenant_initial_data, fill_user_initial_data
from core.api.doc import HELP_TEXT


__all__ = (
    'TenantResource',
)


class RegistrationInfoField(fields.EmbeddedDocumentField):

    def resource_from_data(self, fk_resource, data, request=None, related_obj=None, related_name=None):
        data = dict_strip_unicode_keys(data)
        type_map = self.to_class._meta.polymorphic
        object_type = data.get('resource_type', None)
        if object_type not in type_map:
            raise tastypie_exceptions.BadRequest("Invalid object type.")

        resource = type_map[object_type]()

        fk_bundle = resource.build_bundle(
            data=data,
            request=request
        )

        if related_obj:
            fk_bundle.related_obj = related_obj
            fk_bundle.related_name = related_name

        return resource.full_hydrate(fk_bundle)


class TenantAuthorization(VosaeGenericAuthorization):

    def update_detail(self, object_list, bundle):
        permission_code = self.get_permission(bundle.request, 'change', bundle.obj.__class__)
        try:
            vosae_user = VosaeUser.objects.get(tenant=bundle.obj, email=bundle.request.user.email)
            assert (permission_code is None or vosae_user.has_perm(permission_code))
            return True
        except:
            raise tastypie_exceptions.Unauthorized("You are not allowed to access that resource.")


class TenantResource(RemoveFilesOnReplaceMixinResource, TenantRequiredOnPutMixinResource, VosaeResource):
    TO_REMOVE_ON_REPLACE = ['svg_logo', 'img_logo', 'terms']

    slug = base_fields.CharField(
        attribute='slug',
        readonly=True,
        help_text=HELP_TEXT['tenant']['slug']
    )
    name = base_fields.CharField(
        attribute='name',
        help_text=HELP_TEXT['tenant']['name']
    )
    email = base_fields.CharField(
        attribute='email',
        null=True,
        blank=True,
        help_text=HELP_TEXT['tenant']['email']
    )
    phone = base_fields.CharField(
        attribute='phone',
        null=True,
        blank=True,
        help_text=HELP_TEXT['tenant']['phone']
    )
    fax = base_fields.CharField(
        attribute='fax',
        null=True,
        blank=True,
        help_text=HELP_TEXT['tenant']['fax']
    )

    postal_address = fields.EmbeddedDocumentField(
        embedded='contacts.api.resources.AddressResource',
        attribute='postal_address',
        null=True,
        help_text=HELP_TEXT['tenant']['postal_address']
    )
    billing_address = fields.EmbeddedDocumentField(
        embedded='contacts.api.resources.AddressResource',
        attribute='billing_address',
        null=True,
        help_text=HELP_TEXT['tenant']['billing_address']
    )
    svg_logo = fields.ReferenceField(
        to='core.api.resources.VosaeFileResource',
        attribute='svg_logo',
        null=True,
        blank=True,
        help_text=HELP_TEXT['tenant']['svg_logo']
    )
    img_logo = fields.ReferenceField(
        to='core.api.resources.VosaeFileResource',
        attribute='img_logo',
        null=True,
        blank=True,
        help_text=HELP_TEXT['tenant']['img_logo']
    )
    terms = fields.ReferenceField(
        to='core.api.resources.VosaeFileResource',
        attribute='terms',
        null=True,
        blank=True,
        help_text=HELP_TEXT['tenant']['terms']
    )
    registration_info = RegistrationInfoField(
        embedded='core.api.resources.RegistrationInfoResource',
        attribute='registration_info',
        help_text=HELP_TEXT['tenant']['registration_info']
    )
    report_settings = fields.EmbeddedDocumentField(
        embedded='core.api.resources.ReportSettingsResource',
        attribute='report_settings',
        null=True,
        help_text=HELP_TEXT['tenant']['report_settings']
    )

    class Meta(VosaeResource.Meta):
        queryset = Tenant.objects.all()
        excludes = ('tenant_settings', 'logo_cache')
        authorization = TenantAuthorization()
        list_allowed_methods = ('get', 'post')
        detail_allowed_methods = ('get', 'put')

    def get_object_list(self, request):
        """Filters associated tenants"""
        object_list = super(TenantResource, self).get_object_list(request)
        accessible_tenants = [g[0] for g in request.user.groups.values_list('name')]
        return object_list.filter(slug__in=accessible_tenants)

    def obj_create(self, bundle, **kwargs):
        """
        Some mandatory actions shoud be synchrounous after Tenant creation but
        before returning the response and should not be in `post_save` hooks since
        issuer is required (got from request).

        These actions are:

        - Adding the creator to the Django group (represents the Tenant)
        - Creation of the VosaeUser linked to the tenant
        - Initial data filling
        """
        from core.models import VosaeUser, VosaeGroup
        bundle = super(TenantResource, self).obj_create(bundle, **kwargs)

        # Update django group associated to the Tenant
        group = Group.objects.get(name=bundle.obj.slug)
        group.user_set.add(bundle.request.user)
        group.save()

        # VosaeUser creation
        user = VosaeUser(
            tenant=bundle.obj,
            email=bundle.request.user.email,
            groups=list(VosaeGroup.objects.filter(tenant=bundle.obj))
        ).save()

        # Fill tenant initial data (Tenant and VosaeUser are required)
        fill_tenant_initial_data.delay(bundle.obj, bundle.request.LANGUAGE_CODE)

        # Fill first user initial data (Tenant and VosaeUser are required)
        fill_user_initial_data.delay(user, bundle.request.LANGUAGE_CODE)

        return bundle

    def full_hydrate(self, bundle):
        """Handle specific fields (supported_currencies/default_currency) on creation"""
        if bundle.request.method.lower() != 'post':
            return super(TenantResource, self).full_hydrate(bundle)

        # Set specific fields for creation
        self.fields.update(
            supported_currencies=SupportedCurrenciesListField(
                of='invoicing.api.resources.CurrencyResource',
                attribute=None
            ),
            default_currency=fields.ReferenceField(
                to='invoicing.api.resources.CurrencyResource',
                attribute=None
            )
        )
        self.fields['supported_currencies'].contribute_to_class(self, 'supported_currencies')
        self.fields['default_currency'].contribute_to_class(self, 'default_currency')
        bundle = super(TenantResource, self).full_hydrate(bundle)
        self.fields.pop('supported_currencies', None)
        self.fields.pop('default_currency', None)
        bundle.data.pop('supported_currencies', None)
        bundle.data.pop('default_currency', None)
        return bundle

    def hydrate_supported_currencies(self, bundle):
        bundle.obj.tenant_settings.invoicing.supported_currencies = self.fields['supported_currencies'].hydrate(bundle)
        return bundle

    def hydrate_default_currency(self, bundle):
        value = self.fields['default_currency'].hydrate(bundle)
        bundle.obj.tenant_settings.invoicing.default_currency = value.obj
        return bundle
