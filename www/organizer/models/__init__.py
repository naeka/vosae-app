# -*- coding:Utf-8 -*-

from mongoengine import signals

from organizer.models import embedded
from organizer.models.embedded import *

from organizer.models import calendar
from organizer.models.calendar import *
from organizer.models import calendar_list
from organizer.models.calendar_list import *
from organizer.models import event
from organizer.models.event import *


__all__ = (
    embedded.__all__ +
    calendar.__all__ +
    calendar_list.__all__ +
    event.__all__
)


"""
SIGNALS
"""


signals.pre_save.connect(VosaeCalendar.pre_save, sender=VosaeCalendar)

signals.pre_save.connect(VosaeEvent.pre_save, sender=VosaeEvent)

signals.post_save.connect(VosaeEvent.post_save, sender=VosaeEvent)

signals.post_delete.connect(VosaeEvent.post_delete, sender=VosaeEvent)
