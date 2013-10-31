# -*- coding:Utf-8 -*-

from django.utils.translation import pgettext_lazy
from mongoengine import EmbeddedDocument, fields


__all__ = (
    'Phone',
)


class Phone(EmbeddedDocument):

    """A phone wrapper which can be embedded in any object."""
    TYPES = (
        ("HOME", pgettext_lazy("phone type", "Home")),
        ("WORK", pgettext_lazy("phone type", "Work"))
    )
    SUBTYPES = (
        ("CELL", pgettext_lazy("phone subtype", "Cell")),
        ("FAX", pgettext_lazy("phone subtype", "Fax"))
    )
    COMBINEDTYPES = {
        "HOME": pgettext_lazy("phone type", "Home"),
        "WORK": pgettext_lazy("phone type", "Work"),
        "HOME-CELL": pgettext_lazy("phone type", "Personal cell"),
        "WORK-CELL": pgettext_lazy("phone type", "Work cell"),
        "HOME-FAX": pgettext_lazy("phone type", "Home fax"),
        "WORK-FAX": pgettext_lazy("phone type", "Work fax")
    }

    label = fields.StringField(max_length=64)
    type = fields.StringField(choices=TYPES)
    subtype = fields.StringField(choices=SUBTYPES)
    phone = fields.StringField(required=True, max_length=16)

    def __eq__(self, other):
        """Equal comparison should only be based on fields values"""
        if isinstance(other, Phone) and \
           self.label == other.label and \
           self.type == other.type and \
           self.subtype == other.subtype and \
           self.phone == other.phone:
            return True
        else:
            return False

    def __unicode__(self):
        return self.phone
