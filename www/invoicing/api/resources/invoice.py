# -*- coding:Utf-8 -*-

from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist

from tastypie import fields as base_fields, http
from tastypie.utils import trailing_slash
from tastypie.exceptions import BadRequest
from tastypie_mongoengine import fields

from invoicing.models import Invoice
from invoicing.exceptions import NotCancelableInvoice, NotPayableInvoice
from invoicing.api.resources.invoice_base import InvoiceBaseResource
from invoicing.api.doc import HELP_TEXT
from invoicing import signals as invoicing_signals


__all__ = (
    'InvoiceResource',
)


class InvoiceResource(InvoiceBaseResource):
    state = base_fields.CharField(
        attribute='state',
        readonly=True,
        help_text=HELP_TEXT['invoice']['state']
    )
    paid = base_fields.DecimalField(
        attribute='paid',
        readonly=True,
        help_text=HELP_TEXT['invoice']['paid']
    )
    balance = base_fields.DecimalField(
        attribute='balance',
        readonly=True,
        help_text=HELP_TEXT['invoice']['balance']
    )
    has_temporary_reference = base_fields.BooleanField(
        attribute='has_temporary_reference',
        readonly=True,
        help_text=HELP_TEXT['invoice']['has_temporary_reference']
    )

    payments = fields.ReferencedListField(
        of='invoicing.api.resources.PaymentResource',
        attribute='payments',
        readonly=True,
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoice']['payments']
    )

    class Meta(InvoiceBaseResource.Meta):
        queryset = Invoice.objects.all()
        detail_specific_methods = ('cancel', 'mark_as_registered')

    def prepend_urls(self):
        """Add urls for resources actions."""
        urls = super(InvoiceResource, self).prepend_urls()
        urls.extend((
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/cancel%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('invoice_cancel'), name='api_invoice_cancel'),
        ))
        return urls

    def invoice_cancel(self, request, **kwargs):
        """Cancel the invoice and returns the associated credit note."""
        from invoicing.api.resources.credit_note import CreditNoteResource
        self.method_check(request, allowed=['put'])
        self.is_authenticated(request)
        self.throttle_check(request)

        try:
            bundle = self.build_bundle(request=request)
            obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()

        try:
            credit_note = obj.cancel(request.vosae_user)
            invoicing_signals.post_cancel_invoice.send(obj.__class__, issuer=request.vosae_user, document=obj, credit_note=credit_note)
            credit_note_resource = CreditNoteResource()
            credit_note_resource_bundle = credit_note_resource.build_bundle(obj=credit_note, request=request)
        except NotCancelableInvoice as e:
            raise BadRequest(e)

        self.log_throttled_access(request)

        to_be_serialized = {
            'credit_note_uri': credit_note_resource.get_resource_uri(credit_note_resource_bundle)
        }
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)
