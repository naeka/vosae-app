# -*- coding:Utf-8 -*-

from mongoengine import signals
from timeline.models.base import TimelineEntry
from timeline.models.contacts_entries.contacts_timeline_entry import ContactsTimelineEntry

from timeline.models.contacts_entries import entity_saved
from timeline.models.contacts_entries.entity_saved import *


__all__ = (
    entity_saved.__all__
)


"""
SIGNALS
"""


signals.pre_save.connect(ContactsTimelineEntry.pre_save_contact, sender=ContactSaved)
signals.pre_save.connect(ContactsTimelineEntry.pre_save_organization, sender=OrganizationSaved)

signals.post_save.connect(TimelineEntry.post_save, sender=ContactSaved)
signals.post_save.connect(TimelineEntry.post_save, sender=OrganizationSaved)
