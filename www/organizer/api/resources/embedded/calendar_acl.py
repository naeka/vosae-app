# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import VosaeResource
from organizer.models.embedded.calendar_acl import CalendarAcl, CalendarAclRule
from organizer.api.doc import HELP_TEXT


__all__ = (
    'CalendarAclResource',
    'CalendarAclRuleResource'
)


class CalendarAclRuleResource(VosaeResource):
    role = base_fields.CharField(
        attribute='role',
        help_text=HELP_TEXT['calendar_acl']['role']
    )

    principal = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='principal',
        help_text=HELP_TEXT['calendar_acl']['principal']
    )

    class Meta(VosaeResource.Meta):
        object_class = CalendarAclRule

    def dehydrate_principal(self, bundle):
        # Ugly hack to handle generic references (user/group)
        from core.models import VosaeGroup
        if isinstance(bundle.obj['principal'], VosaeGroup):
            bundle.data['principal'] = bundle.data['principal'].replace('/user/', '/group/')
        return bundle.data['principal']


class CalendarAclResource(VosaeResource):
    rules = fields.EmbeddedListField(
        of='organizer.api.resources.CalendarAclRuleResource',
        attribute='rules',
        full=True,
        help_text=HELP_TEXT['calendar_acl']['rules']
    )

    class Meta(VosaeResource.Meta):
        object_class = CalendarAcl
        excludes = ('read_list', 'write_list', 'negate_list')
