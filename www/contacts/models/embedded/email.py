# -*- coding:Utf-8 -*-

from django.utils.translation import pgettext_lazy
from mongoengine import EmbeddedDocument, fields


__all__ = (
    'Email',
)


class Email(EmbeddedDocument):

    """An e-mail wrapper which can be embedded in any object."""
    TYPES = (
        ("HOME", pgettext_lazy("email type", "Personal")),
        ("WORK", pgettext_lazy("email type", "Work"))
    )

    label = fields.StringField(max_length=64)
    type = fields.StringField(choices=TYPES)
    email = fields.EmailField(required=True, max_length=128)

    def __eq__(self, other):
        """Equal comparison should only be based on fields values"""
        if isinstance(other, Email) and \
           self.label == other.label and \
           self.type == other.type and \
           self.email == other.email:
            return True
        else:
            return False

    def __unicode__(self):
        return self.email
