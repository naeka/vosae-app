# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import TenantResource
from data_liberation.models import Export
from data_liberation.api.doc import HELP_TEXT


__all__ = (
    'ExportResource',
)


class ExportResource(TenantResource):
    created_at = base_fields.DateTimeField(
        attribute='created_at',
        readonly=True,
        help_text=HELP_TEXT['export']['created_at']
    )
    language = base_fields.CharField(
        attribute='language',
        help_text=HELP_TEXT['export']['language']
    )
    documents_types = base_fields.ListField(
        attribute='documents_types',
        help_text=HELP_TEXT['export']['documents_types']
    )
    from_date = base_fields.DateField(
        attribute='from_date',
        null=True,
        blank=True,
        help_text=HELP_TEXT['export']['from_date']
    )
    to_date = base_fields.DateField(
        attribute='to_date',
        null=True,
        blank=True,
        help_text=HELP_TEXT['export']['to_date']
    )

    issuer = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='issuer',
        readonly=True,
        help_text=HELP_TEXT['export']['issuer']
    )
    zipfile = fields.ReferenceField(
        to='core.api.resources.VosaeFileResource',
        attribute='zipfile',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['export']['zipfile']
    )

    class Meta(TenantResource.Meta):
        resource_name = 'export'
        queryset = Export.objects.all()
        list_allowed_methods = ('get', 'post', 'delete')
        detail_allowed_methods = ('get', 'delete')
        excludes = ('tenant',)

    def hydrate(self, bundle):
        """Set issuer on POST, extracted from request"""
        bundle = super(ExportResource, self).hydrate(bundle)
        bundle.obj.issuer = bundle.request.vosae_user
        return bundle
