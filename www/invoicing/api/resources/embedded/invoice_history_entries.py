# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import VosaeResource
from invoicing.models.embedded import invoice_history_entries
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'InvoiceHistoryEntryResource',
    'ActionHistoryEntryResource',
    'ChangedStateHistoryEntryResource',
    'SentHistoryEntryResource',
)


class InvoiceHistoryEntryBaseResource(VosaeResource):
    datetime = base_fields.DateTimeField(
        attribute='datetime',
        readonly=True,
        help_text=HELP_TEXT['history_entry']['datetime']
    )
    issuer = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='issuer',
        readonly=True,
        help_text=HELP_TEXT['history_entry']['issuer']
    )
    revision = base_fields.CharField(
        attribute='revision',
        readonly=True,
        help_text=HELP_TEXT['history_entry']['revision']
    )

    class Meta(VosaeResource.Meta):
        object_class = invoice_history_entries.InvoiceHistoryEntry


class ActionHistoryEntryResource(InvoiceHistoryEntryBaseResource):
    action = base_fields.CharField(
        attribute='action',
        readonly=True,
        help_text=HELP_TEXT['history_entry']['action']
    )

    class Meta(InvoiceHistoryEntryBaseResource.Meta):
        object_class = invoice_history_entries.ActionHistoryEntry


class ChangedStateHistoryEntryResource(InvoiceHistoryEntryBaseResource):
    state = base_fields.CharField(
        attribute='state',
        readonly=True,
        help_text=HELP_TEXT['history_entry']['state']
    )

    class Meta(InvoiceHistoryEntryBaseResource.Meta):
        object_class = invoice_history_entries.ChangedStateHistoryEntry


class SentHistoryEntryResource(InvoiceHistoryEntryBaseResource):
    sent_method = base_fields.CharField(
        attribute='sent_method',
        readonly=True,
        help_text=HELP_TEXT['history_entry']['sent_method']
    )
    sent_to = base_fields.CharField(
        attribute='sent_to',
        readonly=True,
        help_text=HELP_TEXT['history_entry']['sent_to']
    )

    class Meta(InvoiceHistoryEntryBaseResource.Meta):
        object_class = invoice_history_entries.SentHistoryEntry


class InvoiceHistoryEntryResource(InvoiceHistoryEntryBaseResource):

    class Meta(InvoiceHistoryEntryBaseResource.Meta):
        resource_name = 'history_entry'

        polymorphic = {
            'action_history_entry': ActionHistoryEntryResource,
            'changed_state_history_entry': ChangedStateHistoryEntryResource,
            'sent_history_entry': SentHistoryEntryResource,
        }
