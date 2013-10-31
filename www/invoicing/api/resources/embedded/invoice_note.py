# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import VosaeResource
from invoicing.models import InvoiceNote
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'InvoiceNoteResource',
)


class InvoiceNoteResource(VosaeResource):
    datetime = base_fields.DateTimeField(
        attribute='datetime',
        readonly=True,
        help_text=HELP_TEXT['invoice_note']['datetime']
    )
    note = base_fields.CharField(
        attribute='note',
        help_text=HELP_TEXT['invoice_note']['note']
    )

    issuer = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='issuer',
        readonly=True,
        help_text=HELP_TEXT['invoice_note']['issuer']
    )

    class Meta(VosaeResource.Meta):
        object_class = InvoiceNote

    def full_hydrate(self, bundle):
        """Set issuer on POST, extracted from request"""
        bundle = super(InvoiceNoteResource, self).full_hydrate(bundle)
        if bundle.request.method.lower() == 'post':
            bundle.obj.issuer = bundle.request.vosae_user
        return bundle
