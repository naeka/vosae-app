# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import VosaeResource
from organizer.models.embedded.attendee import Attendee
from organizer.api.doc import HELP_TEXT


__all__ = (
    'AttendeeResource',
)


class AttendeeResource(VosaeResource):
    email = base_fields.CharField(
        attribute='email',
        help_text=HELP_TEXT['attendee']['email']
    )
    display_name = base_fields.CharField(
        attribute='display_name',
        null=True,
        blank=True,
        help_text=HELP_TEXT['attendee']['display_name']
    )
    organizer = base_fields.BooleanField(
        attribute='organizer',
        blank=True,
        help_text=HELP_TEXT['attendee']['organizer']
    )
    optional = base_fields.BooleanField(
        attribute='optional',
        blank=True,
        help_text=HELP_TEXT['attendee']['optional']
    )
    response_status = base_fields.CharField(
        attribute='response_status',
        blank=True,
        help_text=HELP_TEXT['attendee']['response_status']
    )
    comment = base_fields.CharField(
        attribute='comment',
        null=True,
        blank=True,
        help_text=HELP_TEXT['attendee']['comment']
    )
    photo_uri = base_fields.CharField(
        attribute='vosae_user__photo_uri',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['attendee']['photo_uri']
    )

    vosae_user = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='vosae_user',
        null=True,
        blank=True,
        help_text=HELP_TEXT['attendee']['vosae_user']
    )

    class Meta(VosaeResource.Meta):
        object_class = Attendee
