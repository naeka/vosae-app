# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import VosaeResource
from vosae_settings.models.core_settings import StorageQuotasSettings, CoreSettings
from vosae_settings.api.doc import HELP_TEXT


__all__ = (
    'CoreSettingsResource',
)


class StorageQuotasSettingsResource(VosaeResource):
    allocated_space = base_fields.IntegerField(
        attribute='allocated_space',
        readonly=True,
        help_text=HELP_TEXT['storage_quotas_settings']['allocated_space']
    )
    used_space = base_fields.IntegerField(
        attribute='used_space',
        readonly=True,
        help_text=HELP_TEXT['storage_quotas_settings']['used_space']
    )

    class Meta:
        object_class = StorageQuotasSettings


class CoreSettingsResource(VosaeResource):
    quotas = fields.EmbeddedDocumentField(
        embedded='vosae_settings.api.resources.core_settings.StorageQuotasSettingsResource',
        attribute='quotas',
        readonly=True,
        help_text=HELP_TEXT['core_settings']['quotas']
    )

    class Meta:
        object_class = CoreSettings
