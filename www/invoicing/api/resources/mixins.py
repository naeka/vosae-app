# -*- coding:Utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist

from tastypie import http
from tastypie.exceptions import BadRequest

from decimal import Decimal, ROUND_HALF_UP
from dateutil.parser import parse

from invoicing import signals as invoicing_signals


__all__ = ('InvoiceMakableResourceMixin',)


class InvoiceMakableResourceMixin(object):

    """Mixin used for both quotations and purchase orders to generate invoices from their current revision"""

    def make_invoice(self, request, **kwargs):
        """Create an invoice from a quotation/purchase order"""
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
        invoicing_signals.post_make_invoice.send(obj.__class__, issuer=request.vosae_user, document=obj, new_document=invoice)
        invoice_resource = InvoiceResource()
        invoice_resource_bundle = invoice_resource.build_bundle(obj=invoice, request=request)

        self.log_throttled_access(request)

        to_be_serialized = {
            'invoice_uri': invoice_resource.get_resource_uri(invoice_resource_bundle)
        }
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)

    def make_down_payment_invoice(self, request, **kwargs):
        """Create a down payment invoice from a quotation/purchase order"""
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
            dp_invoice = obj.make_down_payment_invoice(request.vosae_user, percentage, tax.obj, due_date)
        except Exception as e:
            raise BadRequest(e)
        invoicing_signals.post_make_down_payment_invoice.send(obj.__class__, issuer=request.vosae_user, document=obj, new_document=dp_invoice)
        dp_invoice_resource_bundle = dp_invoice_resource.build_bundle(obj=dp_invoice, request=request)

        self.log_throttled_access(request)

        to_be_serialized = {
            'down_payment_invoice_uri': dp_invoice_resource.get_resource_uri(dp_invoice_resource_bundle)
        }
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)