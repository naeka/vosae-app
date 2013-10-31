# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import TenantResource
from core.models import VosaeGroup
from core.api.doc import HELP_TEXT


__all__ = (
    'VosaeGroupResource',
)


class VosaeGroupResource(TenantResource):
    name = base_fields.CharField(
        attribute='name',
        help_text=HELP_TEXT['vosae_group']['name']
    )
    created_at = base_fields.DateTimeField(
        attribute='created_at',
        readonly=True,
        help_text=HELP_TEXT['vosae_group']['created_at']
    )
    permissions = base_fields.ListField(
        help_text=HELP_TEXT['vosae_group']['permissions']
    )

    created_by = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='created_by',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['vosae_group']['created_by']
    )

    class Meta(TenantResource.Meta):
        resource_name = 'group'
        queryset = VosaeGroup.objects.all()
        list_allowed_methods = ('get', 'post')
        excludes = ('tenant', 'is_admin')

    def full_hydrate(self, bundle):
        """Set the creator on POST"""
        bundle = super(VosaeGroupResource, self).full_hydrate(bundle)
        if bundle.request.method.lower() == 'post':
            bundle.obj.created_by = bundle.request.vosae_user
        return bundle

    def hydrate_permissions(self, bundle):
        """Hydrate the permissions dict from a simple list of granted permissions"""
        if 'permissions' in bundle.data:
            for perm, perm_data in bundle.obj.permissions.perms.iteritems():
                if perm in bundle.data['permissions']:
                    bundle.obj.permissions.perms[perm]['authorization'] = True
                elif bundle.obj.permissions.perms[perm]['authorization'] is True:
                    bundle.obj.permissions.perms[perm]['authorization'] = False
        return bundle

    def dehydrate_permissions(self, bundle):
        """Returns the list of acquired permissions"""
        return list(bundle.obj.permissions.acquired)
