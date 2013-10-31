# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext as _
from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import VosaeIMEXMixinResource
from contacts.api.resources import EntityResource
from contacts.models import Organization
from contacts.api.doc import HELP_TEXT


__all__ = (
    'OrganizationResource',
)


class OrganizationResource(EntityResource, VosaeIMEXMixinResource):
    corporate_name = base_fields.CharField(
        attribute='corporate_name',
        help_text=HELP_TEXT['organization']['corporate_name']
    )

    tags = base_fields.ListField(
        attribute='tags',
        null=True,
        blank=True,
        help_text=HELP_TEXT['organization']['tags']
    )
    contacts = fields.ReferencedListField(
        of='contacts.api.resources.ContactResource',
        attribute='contacts',
        readonly=True,
        null=True,
        blank=True,
        help_text=HELP_TEXT['organization']['contacts']
    )

    class Meta(EntityResource.Meta):
        queryset = Organization.objects.all()

    def prepend_urls(self):
        """Add urls for resources import/export."""
        urls = super(EntityResource, self).prepend_urls()
        urls.extend(VosaeIMEXMixinResource.prepend_urls(self))
        return urls

    def do_import(self, request, serializer, import_buffer):
        """Organizations import"""
        try:
            return serializer.deserialize(import_buffer, self._meta.object_class, request.tenant)
        except:
            pass

    def do_export(self, request, serializer, export_objects):
        """Organizations export"""
        if len(export_objects) == 1:
            filename = export_objects[0].corporate_name
        else:
            filename = _('Organizations')
        return serializer.serialize(export_objects), filename
