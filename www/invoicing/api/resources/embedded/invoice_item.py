# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import VosaeResource
from invoicing.models import InvoiceItem
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'InvoiceItemResource',
)


class InvoiceItemResource(VosaeResource):
    reference = base_fields.CharField(
        attribute='reference',
        help_text=HELP_TEXT['invoice_item']['reference']
    )
    description = base_fields.CharField(
        attribute='description',
        help_text=HELP_TEXT['invoice_item']['description']
    )
    quantity = base_fields.DecimalField(
        attribute='quantity',
        help_text=HELP_TEXT['invoice_item']['quantity']
    )
    unit_price = base_fields.DecimalField(
        attribute='unit_price',
        help_text=HELP_TEXT['invoice_item']['unit_price']
    )
    optional = base_fields.BooleanField(
        attribute='optional',
        help_text=HELP_TEXT['invoice_item']['optional']
    )

    tax = fields.ReferenceField(
        to='invoicing.api.resources.TaxResource',
        attribute='tax',
        null=True,
        help_text=HELP_TEXT['invoice_item']['tax']
    )

    class Meta(VosaeResource.Meta):
        object_class = InvoiceItem
