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
    DEFAULT_TAXES = ()

    business_entity = fields.StringField()
    share_capital = fields.StringField(required=True)

    meta = {
        "allow_inheritance": True
    }

    class Meta:
        report_mandatory_fields = ()

    def get_default_taxes(self):
        return self.DEFAULT_TAXES

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

    def get_legal_paragraphs(self):
        return []


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
        (Decimal('0.21'), u'TVA'),
        (Decimal('0.12'), u'TVA'),
        (Decimal('0.06'), u'TVA')
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
        (Decimal('0.08'), u'TVA'),
        (Decimal('0.038'), u'TVA'),
        (Decimal('0.025'), u'uTVA')
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
    - French "Auto entrepreneur" status flag
    """
    COUNTRY_CODE = 'FR'
    DEFAULT_TAXES = (
        (Decimal('0.20'), u'TVA'),
        (Decimal('0.10'), u'TVA'),
        (Decimal('0.055'), u'TVA'),
        (Decimal('0.021'), u'TVA')
    )

    siret = fields.StringField(required=True, verbose_name=_('SIRET'))
    rcs_number = fields.StringField(required=True, verbose_name=_('RCS number'))
    is_auto_entrepreneur = fields.BooleanField(required=True, default=False)

    class Meta(RegistrationInfo.Meta):
        report_mandatory_fields = RegistrationInfo.Meta.report_mandatory_fields + (
            'share_capital',
            'business_entity',
            'vat_number',
            'siret',
            'rcs_number',
        )

    def get_default_taxes(self):
        if self.is_auto_entrepreneur:
            # "Auto entrepreneurs" are not eligible for VAT
            return (
                (Decimal('0.00'), u'Non applicable'),
            )
        return self.DEFAULT_TAXES

    def get_legal_paragraphs(self):
        paragraphs = super(FRRegistrationInfo, self).get_legal_paragraphs()
        if self.is_auto_entrepreneur:
            paragraphs.append(u'TVA non applicable - article 293 B du CGI')
        return paragraphs


class GBRegistrationInfo(EURegistrationInfoMixin, RegistrationInfo):

    """Great Britain registration infos"""
    COUNTRY_CODE = 'GB'
    DEFAULT_TAXES = (
        (Decimal('0.2'), u'VAT'),
        (Decimal('0.05'), u'VAT')
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
        (Decimal('0.15'), u'TVA'),
        (Decimal('0.12'), u'TVA'),
        (Decimal('0.06'), u'TVA'),
        (Decimal('0.03'), u'TVA')
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
        (Decimal('0.1'), u'Sales tax'),
        (Decimal('0.05'), u'Sales tax')
    )

    class Meta(RegistrationInfo.Meta):
        report_mandatory_fields = RegistrationInfo.Meta.report_mandatory_fields + (
            'share_capital',
        )
