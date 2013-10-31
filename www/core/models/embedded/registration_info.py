# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from mongoengine import EmbeddedDocument, fields
from decimal import Decimal


__all__ = (
    'RegistrationInfo',
    'BERegistrationInfo',
    'CHRegistrationInfo',
    'FRRegistrationInfo',
    'GBRegistrationInfo',
    'LURegistrationInfo',
    'USRegistrationInfo',
)


class RegistrationInfo(EmbeddedDocument):

    """
    Registration info base class composed by informations common to every country such as:

    - Business entity (Inc., Ltd., GmBh, SA, etc.)
    - Share capital
    """
    business_entity = fields.StringField()
    share_capital = fields.StringField(required=True)

    meta = {
        "allow_inheritance": True
    }

    class Meta:
        report_mandatory_fields = ()

    def get_list(self):
        infos = []
        if self.business_entity and self.share_capital:
            infos.append(_("%(business_entity)s with a capital of %(share_capital)s") % {
                'business_entity': self.business_entity,
                'share_capital': self.share_capital
            })
        elif self.business_entity:
            infos.append(self.business_entity)
        elif self.share_capital:
            infos.append(_("With a capital of %(share_capital)s") % {
                'share_capital': self.share_capital
            })
        for field_key, field in self._fields.items():
            if field_key in ['business_entity', 'share_capital']:
                continue
            if getattr(self, field_key, None):
                infos.append(_("%(field_name)s: %(field_value)s") % {
                    'field_name': unicode(field.verbose_name),
                    'field_value': getattr(self, field_key)
                })
        return infos


"""
Regions mixins
"""


class EURegistrationInfoMixin(object):

    """
    Registration info for European Union countries, currently adds:

    - VAT number
    """
    vat_number = fields.StringField(required=True, verbose_name=_('VAT number'))


"""
Localized registration infos
"""


class BERegistrationInfo(EURegistrationInfoMixin, RegistrationInfo):

    """Belgium registration infos"""
    COUNTRY_CODE = 'BE'
    DEFAULT_TAXES = (
        (Decimal('0.21'), 'TVA'),
        (Decimal('0.12'), 'TVA'),
        (Decimal('0.06'), 'TVA')
    )

    class Meta(RegistrationInfo.Meta):
        report_mandatory_fields = RegistrationInfo.Meta.report_mandatory_fields + (
            'share_capital',
            'vat_number',
            'siret',
        )


class CHRegistrationInfo(RegistrationInfo):

    """
    Switzerland registration infos  
    Currently adds:

    - VAT number (since Switzerland is not compound by :class:`~core.models.EURegistrationInfoMixin`)
    """
    COUNTRY_CODE = 'CH'
    DEFAULT_TAXES = (
        (Decimal('0.08'), 'TVA'),
        (Decimal('0.038'), 'TVA'),
        (Decimal('0.025'), 'TVA')
    )

    vat_number = fields.StringField(required=True, verbose_name=_('VAT number'))

    class Meta(RegistrationInfo.Meta):
        report_mandatory_fields = RegistrationInfo.Meta.report_mandatory_fields + (
            'share_capital',
            'vat_number',
            'siret',
        )


class FRRegistrationInfo(EURegistrationInfoMixin, RegistrationInfo):

    """
    France registration infos

    Currently adds:

    - SIRET number
    - RCS number
    """
    COUNTRY_CODE = 'FR'
    DEFAULT_TAXES = (
        (Decimal('0.196'), 'TVA'),
        (Decimal('0.07'), 'TVA'),
        (Decimal('0.055'), 'TVA')
    )

    siret = fields.StringField(required=True, verbose_name=_('SIRET'))
    rcs_number = fields.StringField(required=True, verbose_name=_('RCS number'))

    class Meta(RegistrationInfo.Meta):
        report_mandatory_fields = RegistrationInfo.Meta.report_mandatory_fields + (
            'share_capital',
            'business_entity',
            'vat_number',
            'siret',
            'rcs_number',
        )


class GBRegistrationInfo(EURegistrationInfoMixin, RegistrationInfo):

    """Great Britain registration infos"""
    COUNTRY_CODE = 'GB'
    DEFAULT_TAXES = (
        (Decimal('0.2'), 'VAT'),
        (Decimal('0.05'), 'VAT')
    )

    class Meta(RegistrationInfo.Meta):
        report_mandatory_fields = RegistrationInfo.Meta.report_mandatory_fields + (
            'share_capital',
            'vat_number',
            'siret',
        )


class LURegistrationInfo(EURegistrationInfoMixin, RegistrationInfo):

    """Luxembourg registration infos"""
    COUNTRY_CODE = 'LU'
    DEFAULT_TAXES = (
        (Decimal('0.15'), 'TVA'),
        (Decimal('0.12'), 'TVA'),
        (Decimal('0.06'), 'TVA'),
        (Decimal('0.03'), 'TVA')
    )

    class Meta(RegistrationInfo.Meta):
        report_mandatory_fields = RegistrationInfo.Meta.report_mandatory_fields + (
            'share_capital',
            'vat_number',
            'siret',
        )


class USRegistrationInfo(RegistrationInfo):

    """United States registration infos"""
    COUNTRY_CODE = 'US'
    DEFAULT_TAXES = (
        (Decimal('0.1'), 'Sales tax'),
        (Decimal('0.05'), 'Sales tax')
    )

    class Meta(RegistrationInfo.Meta):
        report_mandatory_fields = RegistrationInfo.Meta.report_mandatory_fields + (
            'share_capital',
        )
