# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields

from core.api.utils import VosaeResource
from core.api.doc import HELP_TEXT
from core.models.embedded.report_settings import ReportSettings


__all__ = (
    'ReportSettingsResource',
)


class ReportSettingsResource(VosaeResource):
    font_name = base_fields.CharField(
        attribute='font_name',
        blank=True,
        help_text=HELP_TEXT['report_settings']['font_name']
    )
    font_size = base_fields.IntegerField(
        attribute='font_size',
        blank=True,
        help_text=HELP_TEXT['report_settings']['font_size']
    )
    font_color = base_fields.CharField(
        attribute='font_color',
        blank=True,
        help_text=HELP_TEXT['report_settings']['font_color']
    )
    base_color = base_fields.CharField(
        attribute='base_color',
        blank=True,
        help_text=HELP_TEXT['report_settings']['base_color']
    )
    force_bw = base_fields.BooleanField(
        attribute='force_bw',
        blank=True,
        help_text=HELP_TEXT['report_settings']['force_bw']
    )
    language = base_fields.CharField(
        attribute='language',
        blank=True,
        help_text=HELP_TEXT['report_settings']['language']
    )

    class Meta(VosaeResource.Meta):
        object_class = ReportSettings
