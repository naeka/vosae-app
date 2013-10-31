# -*- coding:Utf-8 -*-

from mongoengine import EmbeddedDocument, fields

from core.fields import MultipleReferencesField


__all__ = (
    'CalendarAcl',
    'CalendarAclRule'
)


class CalendarAcl(EmbeddedDocument):
    """A calendar ACL"""
    rules = fields.ListField(fields.EmbeddedDocumentField("CalendarAclRule"), required=True)
    read_list = fields.ListField(MultipleReferencesField(document_types=['VosaeUser', 'VosaeGroup']), required=True)
    write_list = fields.ListField(MultipleReferencesField(document_types=['VosaeUser', 'VosaeGroup']))
    negate_list = fields.ListField(MultipleReferencesField(document_types=['VosaeUser', 'VosaeGroup']))

    def genere_rw_list(self):
        """
        Generate a R/W list based on the rules.
        """
        self.read_list = []
        self.write_list = []
        self.negate_list = []
        for rule in self.rules:
            if rule.role is 'NONE':
                self.negate_list.append(rule.principal)
                continue
            if rule.role in CalendarAclRule.READER_ROLES:
                self.read_list.append(rule.principal)
            if rule.role in CalendarAclRule.WRITER_ROLES:
                self.write_list.append(rule.principal)

    def get_owner(self):
        from core.models import VosaeUser
        for rule in self.rules:
            if rule.role == 'OWNER' and isinstance(rule.principal, VosaeUser):
                return rule.principal
        raise ValueError('Calendar has no user owner')


class CalendarAclRule(EmbeddedDocument):
    """A calendar ACL rule, linked to a principal (VosaeUser or VosaeGroup)"""
    BASE_ROLES = ('NONE',)
    READER_ROLES = ('READER', 'WRITER', 'OWNER')
    WRITER_ROLES = ('WRITER', 'OWNER')
    ROLES = tuple(set(BASE_ROLES).union(READER_ROLES, WRITER_ROLES))

    principal = MultipleReferencesField(document_types=['VosaeUser', 'VosaeGroup'], required=True)
    role = fields.StringField(choices=ROLES, required=True)
