# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields

from core.api.utils import VosaeResource
from contacts.models import Email
from contacts.api.doc import HELP_TEXT


__all__ = (
    'EmailResource',
)


class EmailResource(VosaeResource):
    label = base_fields.CharField(
        attribute='label',
        null=True,
        blank=True,
        help_text=HELP_TEXT['email']['label']
    )
    type = base_fields.CharField(
        attribute='type',
        null=True,
        blank=True,
        help_text=HELP_TEXT['email']['type']
    )
    email = base_fields.CharField(
        attribute='email',
        help_text=HELP_TEXT['email']['email']
    )

    class Meta(VosaeResource.Meta):
        object_class = Email
