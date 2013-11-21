# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields

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

    class Meta(InvoiceBaseResource.Meta):
        resource_name = 'credit_note'
        queryset = CreditNote.objects.all()
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        detail_specific_methods = ('cancel',)
