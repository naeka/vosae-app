# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from mongoengine import EmbeddedDocument, fields
import copy


__all__ = (
    'VosaePermissions',
)


class VosaePermissions(EmbeddedDocument):

    """
    Permissions on Vosae.
    """
    PERMISSIONS = {
        'core_access': {'authorization': False, 'module': 'core', 'display_order': 0, 'name': _('Access to the application')},
        'change_appconf': {'authorization': False, 'module': 'core', 'display_order': 1, 'name': _('Can configure application')},
        'see_vosaeuser': {'authorization': False, 'module': 'core', 'display_order': 10, 'name': _('Can see users')},
        'add_vosaeuser': {'authorization': False, 'module': 'core', 'display_order': 11, 'name': _('Can add users')},
        'change_vosaeuser': {'authorization': False, 'module': 'core', 'display_order': 12, 'name': _('Can edit users')},
        'delete_vosaeuser': {'authorization': False, 'module': 'core', 'display_order': 13, 'name': _('Can delete users')},
        'see_vosaegroup': {'authorization': False, 'module': 'core', 'display_order': 20, 'name': _('Can see groups')},
        'add_vosaegroup': {'authorization': False, 'module': 'core', 'display_order': 21, 'name': _('Can add groups')},
        'change_vosaegroup': {'authorization': False, 'module': 'core', 'display_order': 22, 'name': _('Can edit groups')},
        'delete_vosaegroup': {'authorization': False, 'module': 'core', 'display_order': 23, 'name': _('Can delete groups')},
        'see_vosaefile': {'authorization': False, 'module': 'core', 'display_order': 30, 'name': _('Can download files')},
        'add_vosaefile': {'authorization': False, 'module': 'core', 'display_order': 31, 'name': _('Can upload files')},
        'delete_vosaefile': {'authorization': False, 'module': 'core', 'display_order': 32, 'name': _('Can delete files')},

        'organizer_access': {'authorization': False, 'module': 'organizer', 'display_order': 100, 'name': _('Access to the calendar module')},

        'contacts_access': {'authorization': False, 'module': 'contacts', 'display_order': 200, 'name': _('Access to the contacts module')},
        'see_contact': {'authorization': False, 'module': 'contacts', 'display_order': 210, 'name': _('Can see contacts')},
        'add_contact': {'authorization': False, 'module': 'contacts', 'display_order': 211, 'name': _('Can add contacts')},
        'change_contact': {'authorization': False, 'module': 'contacts', 'display_order': 212, 'name': _('Can edit contacts')},
        'delete_contact': {'authorization': False, 'module': 'contacts', 'display_order': 213, 'name': _('Can delete contacts')},

        'invoicing_access': {'authorization': False, 'module': 'invoicing', 'display_order': 300, 'name': _('Access to the invoicing module')},
        'change_invoicingsettings': {'authorization': False, 'module': 'invoicing', 'display_order': 301, 'name': _('Can edit invoicing settings')},
        'see_invoicebase': {'authorization': False, 'module': 'invoicing', 'display_order': 310, 'name': _('Can see invoices')},
        'add_invoicebase': {'authorization': False, 'module': 'invoicing', 'display_order': 311, 'name': _('Can add invoices')},
        'change_invoicebase': {'authorization': False, 'module': 'invoicing', 'display_order': 312, 'name': _('Can edit invoices')},
        'delete_invoicebase': {'authorization': False, 'module': 'invoicing', 'display_order': 313, 'name': _('Can delete/cancel invoices')},
        'transmit_invoicebase': {'authorization': False, 'module': 'invoicing', 'display_order': 314, 'name': _('Can transmit invoices')},
        'post_invoicebase': {'authorization': False, 'module': 'invoicing', 'display_order': 315, 'name': _('Can post invoices')},
        'see_item': {'authorization': False, 'module': 'invoicing', 'display_order': 330, 'name': _('Can see items')},
        'add_item': {'authorization': False, 'module': 'invoicing', 'display_order': 331, 'name': _('Can add items')},
        'change_item': {'authorization': False, 'module': 'invoicing', 'display_order': 332, 'name': _('Can edit items')},
        'delete_item': {'authorization': False, 'module': 'invoicing', 'display_order': 333, 'name': _('Can delete items')},
    }
    _access_perms = None
    _see_perms = None

    acquired = fields.ListField(fields.StringField(choices=PERMISSIONS.keys()))

    def __init__(self, *args, **kwargs):
        super(VosaePermissions, self).__init__(*args, **kwargs)
        self.perms = copy.deepcopy(self.PERMISSIONS)
        for perm in self.acquired:
            if perm not in self.PERMISSIONS.keys():
                continue
            self.perms[perm]['authorization'] = True

    @property
    def access_perms(self):
        if not self._access_perms:
            self._access_perms = tuple(p for p in self.acquired if p.endswith('_access'))
        return self._access_perms

    @property
    def see_perms(self):
        if not self._see_perms:
            self._see_perms = tuple(p for p in self.acquired if p.startswith('see_'))
        return self._see_perms

    def refresh_acquired(self):
        """
        Refresh the acquired list, based on current permissions
        """
        self.acquired = [perm for perm, perm_data in self.perms.iteritems() if perm_data.get('authorization') is True]

    def by_module(self, module):
        """
        List :class:`~core.models.VosaePermissions` module per module.
        """
        module_perms = {}
        for key, perm in self.perms.iteritems():
            if perm["module"] == module:
                module_perms[key] = perm
        return module_perms

    def merge_group(self, permissions):
        """
        Merge a **group** :class:`~core.models.VosaePermissions` object into the current one.
        """
        for key in permissions.acquired:
            if key in self.perms:
                self.perms[key]["authorization"] = True

    def merge_groups(self, groups):
        """
        Recursively process merging of groups permissions.
        """
        for group in groups:
            self.merge_group(group.permissions)

    def merge_user(self, specific_permissions):
        """
        Merge a **user** :class:`~core.models.VosaePermissions` object into the current one.
        """
        for key, perm in specific_permissions.iteritems():
            if key in self.perms:
                self.perms[key]["authorization"] = perm

    def merge_groups_and_user(self, groups, user):
        """
        Merge group and user perms into the current one.
        """
        self.perms = copy.deepcopy(self.PERMISSIONS)
        self.merge_groups(groups)
        self.merge_user(user.specific_permissions)
