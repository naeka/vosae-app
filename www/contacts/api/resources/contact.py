# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext as _
from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import VosaeIMEXMixinResource
from contacts.api.resources import EntityResource
from contacts.models import Contact
from contacts.api.doc import HELP_TEXT


__all__ = (
    'ContactResource',
)


class ContactResource(EntityResource, VosaeIMEXMixinResource):
    name = base_fields.CharField(
        attribute='name',
        help_text=HELP_TEXT['contact']['name']
    )
    firstname = base_fields.CharField(
        attribute='firstname',
        help_text=HELP_TEXT['contact']['firstname']
    )
    additional_names = base_fields.CharField(
        attribute='additional_names',
        null=True,
        blank=True,
        help_text=HELP_TEXT['contact']['additional_names']
    )
    civility = base_fields.CharField(
        attribute='civility',
        null=True,
        blank=True,
        help_text=HELP_TEXT['contact']['civility']
    )
    birthday = base_fields.DateField(
        attribute='birthday',
        null=True,
        blank=True,
        help_text=HELP_TEXT['contact']['birthday']
    )
    role = base_fields.CharField(
        attribute='role',
        null=True,
        blank=True,
        help_text=HELP_TEXT['contact']['role']
    )

    organization = fields.ReferenceField(
        to='contacts.api.resources.OrganizationResource',
        attribute='organization',
        null=True,
        blank=True,
        full=False,
        help_text=HELP_TEXT['contact']['organization']
    )

    class Meta(EntityResource.Meta):
        queryset = Contact.objects.all()

    def prepend_urls(self):
        """Add urls for resources import/export."""
        urls = super(ContactResource, self).prepend_urls()
        urls.extend(VosaeIMEXMixinResource.prepend_urls(self))
        return urls

    def do_import(self, request, serializer, import_buffer):
        """Contacts import"""
        try:
            return serializer.deserialize(import_buffer, self._meta.object_class, request.tenant)
        except:
            pass

    def do_export(self, request, serializer, export_objects):
        """Contacts export"""
        if len(export_objects) == 1:
            filename = export_objects[0].get_full_name()
        else:
            filename = _('Contacts')
        return serializer.serialize(export_objects), filename
