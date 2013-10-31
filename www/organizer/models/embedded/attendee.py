# -*- coding:Utf-8 -*-

from mongoengine import EmbeddedDocument, fields


__all__ = (
    'Attendee',
)


class Attendee(EmbeddedDocument):
    """Represent event's attendees"""
    RESPONSE_STATUTES = (
        ('NEEDS-ACTION'),
        ('DECLINED'),
        ('TENTATIVE'),
        ('ACCEPTED')
    )

    email = fields.EmailField(required=True)
    display_name = fields.StringField(max_length=128)
    organizer = fields.BooleanField(default=False)
    vosae_user = fields.ReferenceField("VosaeUser")
    optional = fields.BooleanField(default=False)
    response_status = fields.StringField(required=True, choices=RESPONSE_STATUTES, default='NEEDS-ACTION')
    comment = fields.StringField(max_length=1024)

    def __unicode__(self):
        return self.display_name
