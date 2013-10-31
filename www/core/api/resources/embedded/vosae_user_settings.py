# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields

from core.api.utils import VosaeResource
from core.api.doc import HELP_TEXT
from core.models import VosaeUserSettings


__all__ = (
    'VosaeUserSettingsResource',
)


class VosaeUserSettingsResource(VosaeResource):
    language_code = base_fields.CharField(
        attribute='language_code',
        null=True,
        blank=True,
        help_text=HELP_TEXT['vosae_user_settings']['language_code']
    )
    gravatar_email = base_fields.CharField(
        attribute='gravatar_email',
        null=True,
        blank=True,
        help_text=HELP_TEXT['vosae_user_settings']['gravatar_email']
    )
    email_signature = base_fields.CharField(
        attribute='email_signature',
        null=True,
        blank=True,
        help_text=HELP_TEXT['vosae_user_settings']['email_signature']
    )

    class Meta(VosaeResource.Meta):
        object_class = VosaeUserSettings
