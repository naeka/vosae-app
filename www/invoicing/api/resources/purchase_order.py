# -*- coding:Utf-8 -*-

from django.conf.urls import url

from tastypie import fields as base_fields
from tastypie.utils import trailing_slash

from invoicing.models import PurchaseOrder
from invoicing.api.resources.invoice_base import InvoiceBaseResource
from invoicing.api.resources.mixins import InvoiceMakableResourceMixin
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'PurchaseOrderResource',
)


class PurchaseOrderResource(InvoiceBaseResource, InvoiceMakableResourceMixin):
    state = base_fields.CharField(
        attribute='state',
        readonly=True,
        help_text=HELP_TEXT['purchase_order']['state']
    )

    class Meta(InvoiceBaseResource.Meta):
        resource_name = 'purchase_order'
        queryset = PurchaseOrder.objects.all()
        detail_specific_methods = ('make_down_payment_invoice', 'make_invoice', 'mark_as_awaiting_approval')

    def prepend_urls(self):
        """Add urls for resources actions."""
        urls = super(PurchaseOrderResource, self).prepend_urls()
        urls.extend((
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/make_invoice%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('make_invoice'), name='api_quotation_make_invoice'),
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/make_down_payment_invoice%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('make_down_payment_invoice'), name='api_quotation_make_down_payment_invoice'),
        ))
        return urls
