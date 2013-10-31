# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields

from core.api.utils import VosaeResource
from contacts.models import Phone
from contacts.api.doc import HELP_TEXT


__all__ = (
    'PhoneResource',
)


class PhoneResource(VosaeResource):
    label = base_fields.CharField(
        attribute='label',
        null=True,
        blank=True,
        help_text=HELP_TEXT['phone']['label']
    )
    type = base_fields.CharField(
        attribute='type',
        null=True,
        blank=True,
        help_text=HELP_TEXT['phone']['type']
    )
    subtype = base_fields.CharField(
        attribute='subtype',
        null=True,
        blank=True,
        help_text=HELP_TEXT['phone']['subtype']
    )
    phone = base_fields.CharField(
        attribute='phone',
        help_text=HELP_TEXT['phone']['phone']
    )

    class Meta(VosaeResource.Meta):
        object_class = Phone
