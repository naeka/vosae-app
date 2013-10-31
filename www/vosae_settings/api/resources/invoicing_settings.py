# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import VosaeResource
from vosae_settings.models.invoicing_settings import InvoicingNumberingSettings, InvoicingSettings
from vosae_settings.api.doc import HELP_TEXT
from vosae_settings.fields import SupportedCurrenciesListField


__all__ = (
    'TenantSettingsResource',
)


class InvoicingNumberingSettingsResource(VosaeResource):
    scheme = base_fields.CharField(
        attribute='scheme',
        help_text=HELP_TEXT['invoicing_numbering_settings']['scheme']
    )
    separator = base_fields.CharField(
        attribute='separator',
        help_text=HELP_TEXT['invoicing_numbering_settings']['separator']
    )
    fy_reset = base_fields.BooleanField(
        attribute='fy_reset',
        help_text=HELP_TEXT['invoicing_numbering_settings']['fy_reset']
    )

    class Meta:
        object_class = InvoicingNumberingSettings
        excludes = ('all_time_credit_note_counter', 'all_time_invoice_counter', 'all_time_quotation_counter',
                    'fy_credit_note_counter', 'fy_invoice_counter', 'fy_quotation_counter')


class InvoicingSettingsResource(VosaeResource):
    fy_start_month = base_fields.IntegerField(
        attribute='fy_start_month',
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoicing_settings']['fy_start_month']
    )
    inv_taxes_application = base_fields.CharField(
        attribute='inv_taxes_application',
        help_text=HELP_TEXT['invoicing_settings']['inv_taxes_application']
    )
    quotation_validity = base_fields.CharField(
        attribute='quotation_validity',
        help_text=HELP_TEXT['invoicing_settings']['quotation_validity']
    )
    payment_conditions = base_fields.CharField(
        attribute='payment_conditions',
        help_text=HELP_TEXT['invoicing_settings']['payment_conditions']
    )
    custom_payment_conditions = base_fields.CharField(
        attribute='custom_payment_conditions',
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoicing_settings']['custom_payment_conditions']
    )
    late_fee_rate = base_fields.DecimalField(
        attribute='late_fee_rate',
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoicing_settings']['late_fee_rate']
    )
    accepted_payment_types = base_fields.ListField(
        attribute='accepted_payment_types',
        help_text=HELP_TEXT['invoicing_settings']['accepted_payment_types']
    )
    down_payment_percent = base_fields.DecimalField(
        attribute='down_payment_percent',
        help_text=HELP_TEXT['invoicing_settings']['down_payment_percent']
    )
    automatic_reminders = base_fields.BooleanField(
        attribute='automatic_reminders',
        help_text=HELP_TEXT['invoicing_settings']['automatic_reminders']
    )
    automatic_reminders_text = base_fields.CharField(
        attribute='automatic_reminders_text',
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoicing_settings']['automatic_reminders_text']
    )
    automatic_reminders_send_copy = base_fields.BooleanField(
        attribute='automatic_reminders_send_copy',
        help_text=HELP_TEXT['invoicing_settings']['automatic_reminders_send_copy']
    )

    supported_currencies = SupportedCurrenciesListField(
        of='invoicing.api.resources.CurrencyResource',
        attribute='supported_currencies',
        help_text=HELP_TEXT['invoicing_settings']['supported_currencies']
    )
    default_currency = fields.ReferenceField(
        to='invoicing.api.resources.CurrencyResource',
        attribute='default_currency',
        help_text=HELP_TEXT['invoicing_settings']['default_currency']
    )
    numbering = fields.EmbeddedDocumentField(
        embedded='vosae_settings.api.resources.invoicing_settings.InvoicingNumberingSettingsResource',
        attribute='numbering',
        help_text=HELP_TEXT['invoicing_settings']['numbering']
    )

    class Meta:
        object_class = InvoicingSettings
