# -*- coding:Utf-8 -*-

from timeline.models.base import TimelineEntry


__all__ = (
    'ContactsTimelineEntry',
)


class ContactsTimelineEntry(TimelineEntry):

    meta = {
        "allow_inheritance": True
    }

    @classmethod
    def pre_save_contact(self, sender, document, **kwargs):
        mandatory_perms = document.contact._meta.get('vosae_mandatory_permissions', ())
        for perm in mandatory_perms:
            if perm.endswith('_access'):
                document.access_permission = perm
                break
        if 'vosae_timeline_permission' in document.contact._meta:
            document.see_permission = document.contact._meta.get('vosae_timeline_permission')
        document.module = 'contacts'

    @classmethod
    def pre_save_organization(self, sender, document, **kwargs):
        mandatory_perms = document.organization._meta.get('vosae_mandatory_permissions', ())
        for perm in mandatory_perms:
            if perm.endswith('_access'):
                document.access_permission = perm
                break
        if 'vosae_timeline_permission' in document.organization._meta:
            document.see_permission = document.organization._meta.get('vosae_timeline_permission')
        document.module = 'contacts'
