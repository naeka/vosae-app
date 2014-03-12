# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import VosaeResource, TagsStripper, BASIC_TAGS
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
    is_translatable = base_fields.BooleanField(
        attribute='is_translatable',
        readonly=True,
        help_text=HELP_TEXT['invoice_item']['is_translatable']
    )

    tax = fields.ReferenceField(
        to='invoicing.api.resources.TaxResource',
        attribute='tax',
        null=True,
        help_text=HELP_TEXT['invoice_item']['tax']
    )

    class Meta(VosaeResource.Meta):
        object_class = InvoiceItem

    def hydrate_description(self, bundle):
        parser = TagsStripper(allowed_tags=BASIC_TAGS)
        parser.feed(bundle.data['description'])
        bundle.data['description'] = parser.get_data()
        return bundle
