# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from invoicing.models import DownPaymentInvoice
from invoicing.api.resources.invoice import InvoiceResource
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'DownPaymentInvoiceResource',
)


class DownPaymentInvoiceResource(InvoiceResource):
    state = base_fields.CharField(
        attribute='state',
        readonly=True,
        help_text=HELP_TEXT['downpayment']['state']
    )
    percentage = base_fields.DecimalField(
        attribute='percentage',
        help_text=HELP_TEXT['downpayment']['percentage']
    )

    tax_applied = fields.ReferenceField(
        to='invoicing.api.resources.TaxResource',
        attribute='tax_applied',
        help_text=HELP_TEXT['downpayment']['tax_applied']
    )

    class Meta(InvoiceResource.Meta):
        resource_name = 'down_payment_invoice'
        queryset = DownPaymentInvoice.objects.all()
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        detail_specific_methods = ('cancel',)
