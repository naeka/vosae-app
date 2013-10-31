# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields
from core.api.utils import (
    TenantResource,
    MultipartMixinResource,
)
from core.models import VosaeFile
from core.api.doc import HELP_TEXT
from vosae_utils.pipeline import FilePipeline


__all__ = (
    'VosaeFileResource',
)


class VosaeFileResource(MultipartMixinResource, TenantResource):
    download_link = base_fields.CharField(
        attribute='download_link',
        readonly=True,
        help_text=HELP_TEXT['vosae_file']['download_link']
    )
    stream_link = base_fields.CharField(
        attribute='stream_link',
        readonly=True,
        help_text=HELP_TEXT['vosae_file']['stream_link']
    )
    name = base_fields.CharField(
        attribute='name',
        readonly=True,
        help_text=HELP_TEXT['vosae_file']['name']
    )
    size = base_fields.IntegerField(
        attribute='size',
        readonly=True,
        help_text=HELP_TEXT['vosae_file']['size']
    )
    sha1_checksum = base_fields.CharField(
        attribute='sha1_checksum',
        readonly=True,
        help_text=HELP_TEXT['vosae_file']['sha1_checksum']
    )
    ttl = base_fields.IntegerField(
        attribute='ttl',
        null=True,
        blank=True,
        help_text=HELP_TEXT['vosae_file']['ttl']
    )
    created_at = base_fields.DateTimeField(
        attribute='created_at',
        readonly=True,
        help_text=HELP_TEXT['vosae_file']['created_at']
    )
    modified_at = base_fields.DateTimeField(
        attribute='modified_at',
        readonly=True,
        help_text=HELP_TEXT['vosae_file']['modified_at']
    )

    issuer = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='issuer',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['vosae_file']['issuer']
    )

    class Meta(TenantResource.Meta):
        resource_name = 'file'
        queryset = VosaeFile.objects.all()
        list_allowed_methods = ('post',)
        fields = ('id', 'issuer', 'name', 'size', 'sha1_checksum', 'ttl', 'created_at', 'modified_at', 'resource_uri')

    def hydrate(self, bundle):
        """Handle pipeline operations"""
        bundle = super(VosaeFileResource, self).hydrate(bundle)
        bundle.obj.issuer = bundle.request.vosae_user
        bundle.obj.uploaded_file = bundle.data.get('uploaded_file')
        pipeline = bundle.data.get('pipeline', None)
        if pipeline:
            pipeline = self._meta.serializer.deserialize(pipeline, format='application/json')
            bundle.obj.uploaded_file = FilePipeline(bundle.obj.uploaded_file, pipeline)
        return bundle

    def dehydrate(self, bundle):
        """Removes extra fields from the response, if exists"""
        bundle = super(VosaeFileResource, self).dehydrate(bundle)
        if 'uploaded_file' in bundle.data:
            del bundle.data['uploaded_file']
        if 'pipeline' in bundle.data:
            del bundle.data['pipeline']
        return bundle
