# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import TenantResource
from invoicing.models import (
    Payment, InvoicePayment, DownPaymentInvoicePayment
)
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'PaymentResource',
)


class PaymentBaseResource(TenantResource):
    issued_at = base_fields.DateTimeField(
        attribute='issued_at',
        readonly=True,
        help_text=HELP_TEXT['payment']['issued_at']
    )
    date = base_fields.DateField(
        attribute='date',
        help_text=HELP_TEXT['payment']['date']
    )
    amount = base_fields.DecimalField(
        attribute='amount',
        help_text=HELP_TEXT['payment']['amount']
    )
    type = base_fields.CharField(
        attribute='type',
        blank=True,
        help_text=HELP_TEXT['payment']['type']
    )
    note = base_fields.CharField(
        attribute='note',
        null=True,
        blank=True,
        help_text=HELP_TEXT['payment']['note']
    )

    issuer = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='issuer',
        readonly=True,
        help_text=HELP_TEXT['payment']['issuer']
    )
    currency = fields.ReferenceField(
        to='invoicing.api.resources.CurrencyResource',
        attribute='currency',
        help_text=HELP_TEXT['payment']['currency']
    )

    class Meta(TenantResource.Meta):
        excludes = ('tenant',)
        list_allowed_methods = ('post')
        detail_allowed_methods = ('get', 'delete',)


class InvoicePaymentResource(PaymentBaseResource):
    related_to = fields.ReferenceField(
        to='invoicing.api.resources.InvoiceResource',
        attribute='related_to',
        help_text=HELP_TEXT['payment']['invoice']
    )

    class Meta(PaymentBaseResource.Meta):
        queryset = InvoicePayment.objects.all()


class DownPaymentInvoicePaymentResource(PaymentBaseResource):
    related_to = fields.ReferenceField(
        to='invoicing.api.resources.DownPaymentInvoiceResource',
        attribute='related_to',
        help_text=HELP_TEXT['payment']['down_payment_invoice']
    )

    class Meta(PaymentBaseResource.Meta):
        queryset = DownPaymentInvoicePayment.objects.all()


class PaymentResource(PaymentBaseResource):

    class Meta(PaymentBaseResource.Meta):
        queryset = Payment.objects.all()

        polymorphic = {
            'payment': 'self',
            'invoice_payment': InvoicePaymentResource,
            'down_payment_invoice_payment': DownPaymentInvoicePaymentResource
        }

    def full_hydrate(self, bundle):
        """Set issuer on POST, extracted from request"""
        bundle = super(PaymentResource, self).full_hydrate(bundle)
        if bundle.request.method.lower() == 'post':
            bundle.obj.issuer = bundle.request.vosae_user
        return bundle
