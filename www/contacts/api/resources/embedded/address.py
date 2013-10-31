# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields

from core.api.utils import VosaeResource
from contacts.models import Address
from contacts.api.doc import HELP_TEXT


__all__ = (
    'AddressResource',
)


class AddressResource(VosaeResource):
    label = base_fields.CharField(
        attribute='label',
        null=True,
        blank=True,
        help_text=HELP_TEXT['address']['label']
    )
    type = base_fields.CharField(
        attribute='type',
        null=True,
        blank=True,
        help_text=HELP_TEXT['address']['type']
    )
    postoffice_box = base_fields.CharField(
        attribute='postoffice_box',
        null=True,
        blank=True,
        help_text=HELP_TEXT['address']['postoffice_box']
    )
    street_address = base_fields.CharField(
        attribute='street_address',
        help_text=HELP_TEXT['address']['street_address']
    )
    extended_address = base_fields.CharField(
        attribute='extended_address',
        null=True,
        blank=True,
        help_text=HELP_TEXT['address']['extended_address']
    )
    postal_code = base_fields.CharField(
        attribute='postal_code',
        null=True,
        blank=True,
        help_text=HELP_TEXT['address']['postal_code']
    )
    city = base_fields.CharField(
        attribute='city',
        null=True,
        blank=True,
        help_text=HELP_TEXT['address']['city']
    )
    state = base_fields.CharField(
        attribute='state',
        null=True,
        blank=True,
        help_text=HELP_TEXT['address']['state']
    )
    country = base_fields.CharField(
        attribute='country',
        null=True,
        blank=True,
        help_text=HELP_TEXT['address']['country']
    )

    class Meta(VosaeResource.Meta):
        object_class = Address
