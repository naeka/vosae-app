# -*- coding:Utf-8 -*-

from timeline.models.base import TimelineEntry


__all__ = (
    'InvoicingTimelineEntry',
)


class InvoicingTimelineEntry(TimelineEntry):

    meta = {
        "allow_inheritance": True
    }

    @classmethod
    def pre_save_quotation(self, sender, document, **kwargs):
        mandatory_perms = document.quotation._meta.get('vosae_mandatory_permissions', ())
        for perm in mandatory_perms:
            if perm.endswith('_access'):
                document.access_permission = perm
                break
        if 'vosae_timeline_permission' in document.quotation._meta:
            document.see_permission = document.quotation._meta.get('vosae_timeline_permission')
        document.module = 'invoicing'

    @classmethod
    def pre_save_purchase_order(self, sender, document, **kwargs):
        mandatory_perms = document.purchase_order._meta.get('vosae_mandatory_permissions', ())
        for perm in mandatory_perms:
            if perm.endswith('_access'):
                document.access_permission = perm
                break
        if 'vosae_timeline_permission' in document.purchase_order._meta:
            document.see_permission = document.purchase_order._meta.get('vosae_timeline_permission')
        document.module = 'invoicing'

    @classmethod
    def pre_save_invoice(self, sender, document, **kwargs):
        mandatory_perms = document.invoice._meta.get('vosae_mandatory_permissions', ())
        for perm in mandatory_perms:
            if perm.endswith('_access'):
                document.access_permission = perm
                break
        if 'vosae_timeline_permission' in document.invoice._meta:
            document.see_permission = document.invoice._meta.get('vosae_timeline_permission')
        document.module = 'invoicing'

    @classmethod
    def pre_save_down_payment_invoice(self, sender, document, **kwargs):
        mandatory_perms = document.down_payment_invoice._meta.get('vosae_mandatory_permissions', ())
        for perm in mandatory_perms:
            if perm.endswith('_access'):
                document.access_permission = perm
                break
        if 'vosae_timeline_permission' in document.down_payment_invoice._meta:
            document.see_permission = document.down_payment_invoice._meta.get('vosae_timeline_permission')
        document.module = 'invoicing'

    @classmethod
    def pre_save_credit_note(self, sender, document, **kwargs):
        mandatory_perms = document.credit_note._meta.get('vosae_mandatory_permissions', ())
        for perm in mandatory_perms:
            if perm.endswith('_access'):
                document.access_permission = perm
                break
        if 'vosae_timeline_permission' in document.credit_note._meta:
            document.see_permission = document.credit_note._meta.get('vosae_timeline_permission')
        document.module = 'invoicing'
