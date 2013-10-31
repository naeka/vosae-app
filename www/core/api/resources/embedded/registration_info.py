# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields

from core.api.utils import VosaeResource
from core.api.doc import HELP_TEXT
from core.models.embedded.registration_info import (
    RegistrationInfo,
    BERegistrationInfo,
    CHRegistrationInfo,
    FRRegistrationInfo,
    GBRegistrationInfo,
    LURegistrationInfo,
    USRegistrationInfo,
)


__all__ = (
    'RegistrationInfoResource',
    'BERegistrationInfoResource',
    'CHRegistrationInfoResource',
    'FRRegistrationInfoResource',
    'GBRegistrationInfoResource',
    'LURegistrationInfoResource',
    'USRegistrationInfoResource',
)


class RegistrationInfoResourceMixin(VosaeResource):
    business_entity = base_fields.CharField(
        attribute='business_entity',
        null=True,
        blank=True,
        help_text=HELP_TEXT['registration_info']['business_entity']
    )
    share_capital = base_fields.CharField(
        attribute='share_capital',
        help_text=HELP_TEXT['registration_info']['share_capital']
    )


class EURegistrationInfoResourceMixin(VosaeResource):
    vat_number = base_fields.CharField(
        attribute='vat_number',
        help_text=HELP_TEXT['registration_info']['vat_number']
    )


class BERegistrationInfoResource(RegistrationInfoResourceMixin, EURegistrationInfoResourceMixin):

    class Meta(VosaeResource.Meta):
        object_class = BERegistrationInfo


class CHRegistrationInfoResource(RegistrationInfoResourceMixin):
    vat_number = base_fields.CharField(
        attribute='vat_number',
        help_text=HELP_TEXT['registration_info']['vat_number']
    )

    class Meta(VosaeResource.Meta):
        object_class = CHRegistrationInfo


class FRRegistrationInfoResource(RegistrationInfoResourceMixin, EURegistrationInfoResourceMixin):
    siret = base_fields.CharField(
        attribute='siret',
        help_text=HELP_TEXT['registration_info']['siret']
    )
    rcs_number = base_fields.CharField(
        attribute='rcs_number',
        help_text=HELP_TEXT['registration_info']['rcs_number']
    )

    class Meta(VosaeResource.Meta):
        object_class = FRRegistrationInfo


class GBRegistrationInfoResource(RegistrationInfoResourceMixin, EURegistrationInfoResourceMixin):

    class Meta(VosaeResource.Meta):
        object_class = GBRegistrationInfo


class LURegistrationInfoResource(RegistrationInfoResourceMixin, EURegistrationInfoResourceMixin):

    class Meta(VosaeResource.Meta):
        object_class = LURegistrationInfo


class USRegistrationInfoResource(RegistrationInfoResourceMixin):

    class Meta(VosaeResource.Meta):
        object_class = USRegistrationInfo


class RegistrationInfoResource(VosaeResource):

    class Meta(VosaeResource.Meta):
        object_class = RegistrationInfo
        polymorphic = {
            'be_registration_info': BERegistrationInfoResource,
            'ch_registration_info': CHRegistrationInfoResource,
            'fr_registration_info': FRRegistrationInfoResource,
            'gb_registration_info': GBRegistrationInfoResource,
            'lu_registration_info': LURegistrationInfoResource,
            'us_registration_info': USRegistrationInfoResource,
        }
