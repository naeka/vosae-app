# -*- coding:Utf-8 -*-

from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist

from tastypie import fields as base_fields, http
from tastypie.utils import trailing_slash
from tastypie.exceptions import BadRequest
from tastypie_mongoengine import fields

from decimal import Decimal, ROUND_HALF_UP
from dateutil.parser import parse

from invoicing.models import Quotation
from invoicing.api.resources.invoice_base import InvoiceBaseResource
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'QuotationResource',
)


class QuotationResource(InvoiceBaseResource):
    state = base_fields.CharField(
        attribute='state',
        readonly=True,
        help_text=HELP_TEXT['quotation']['state']
    )

    related_invoice = fields.ReferenceField(
        to='invoicing.api.resources.InvoiceResource',
        attribute='related_invoice',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['quotation']['related_invoice']
    )
    related_invoices_cancelled = fields.ReferencedListField(
        of='invoicing.api.resources.InvoiceResource',
        attribute='related_invoices_cancelled',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['quotation']['related_invoices_cancelled']
    )
    down_payments = fields.ReferencedListField(
        of='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='down_payments',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['quotation']['down_payments']
    )

    class Meta(InvoiceBaseResource.Meta):
        queryset = Quotation.objects.all()
        detail_specific_methods = ('make_down_payment_invoice', 'make_invoice', 'mark_as_awaiting_approval')

    def prepend_urls(self):
        """Add urls for resources actions."""
        urls = super(QuotationResource, self).prepend_urls()
        urls.extend((
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/make_invoice%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('make_invoice'), name='api_quotation_make_invoice'),
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/make_down_payment_invoice%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('make_down_payment_invoice'), name='api_quotation_make_down_payment_invoice'),
        ))
        return urls

    def make_invoice(self, request, **kwargs):
        """Create an invoice from a quotation"""
        from invoicing.api.resources.invoice import InvoiceResource
        self.method_check(request, allowed=['put'])
        self.is_authenticated(request)
        self.throttle_check(request)

        try:
            bundle = self.build_bundle(request=request)
            obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()

        invoice = obj.make_invoice(request.vosae_user)
        invoice_resource = InvoiceResource()
        invoice_resource_bundle = invoice_resource.build_bundle(obj=invoice, request=request)

        self.log_throttled_access(request)

        to_be_serialized = {
            'invoice_uri': invoice_resource.get_resource_uri(invoice_resource_bundle)
        }
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)

    def make_down_payment_invoice(self, request, **kwargs):
        """Create a down payment invoice from a quotation"""
        from invoicing.api.resources.down_payment_invoice import DownPaymentInvoiceResource
        from tastypie.bundle import Bundle
        self.method_check(request, allowed=['put'])
        self.is_authenticated(request)
        self.throttle_check(request)

        try:
            bundle = self.build_bundle(request=request)
            obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()

        dp_invoice_resource = DownPaymentInvoiceResource()
        try:
            dp_data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
            percentage = Decimal(dp_data.get('percentage')).quantize(Decimal('1.0000'), ROUND_HALF_UP)
            due_date = parse(dp_data.get('due_date'))
            tax_bundle = Bundle(request=request, data=dp_data)
            tax = dp_invoice_resource.fields['tax_applied'].hydrate(tax_bundle)
            if hasattr(due_date, 'hour'):
                due_date = due_date.date()
        except:
            raise BadRequest('Invalid down payment parameters.')

        try:
            dp_invoice = obj.make_down_payment(request.vosae_user, percentage, tax.obj, due_date)
        except Exception as e:
            raise BadRequest(e)
        dp_invoice_resource_bundle = dp_invoice_resource.build_bundle(obj=dp_invoice, request=request)

        self.log_throttled_access(request)

        to_be_serialized = {
            'down_payment_invoice_uri': dp_invoice_resource.get_resource_uri(dp_invoice_resource_bundle)
        }
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)
