# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from invoicing.models import CreditNote
from invoicing.api.resources.invoice_base import InvoiceBaseResource
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'CreditNoteResource',
)


class CreditNoteResource(InvoiceBaseResource):
    state = base_fields.CharField(
        attribute='state',
        readonly=True,
        help_text=HELP_TEXT['creditnote']['state']
    )

    current_revision = fields.EmbeddedDocumentField(
        embedded='invoicing.api.resources.CreditNoteRevisionResource',
        attribute='current_revision',
        help_text=HELP_TEXT['creditnote']['current_revision']
    )
    revisions = fields.EmbeddedListField(
        of='invoicing.api.resources.CreditNoteRevisionResource',
        attribute='revisions',
        readonly=True,
        null=True,
        blank=True,
        help_text=HELP_TEXT['creditnote']['revisions']
    )
    related_to = fields.ReferenceField(
        to='invoicing.api.resources.InvoiceResource',
        attribute='related_to',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['creditnote']['related_to']
    )

    class Meta(InvoiceBaseResource.Meta):
        resource_name = 'credit_note'
        queryset = CreditNote.objects.all()
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        detail_specific_methods = ('cancel',)

    def dehydrate_related_to(self, bundle):
        from invoicing.api.resources import DownPaymentInvoiceResource, InvoiceResource
        try:
            if bundle.obj.related_to.is_down_payment_invoice():
                resource = DownPaymentInvoiceResource()
            elif bundle.obj.related_to.is_invoice():
                resource = InvoiceResource()
            resource_bundle = resource.build_bundle(obj=bundle.obj.related_to, request=bundle.request)
            return resource.get_resource_uri(resource_bundle)
        except:
            return
