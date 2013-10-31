# -*- coding:Utf-8 -*-

from organizer.api.resources.embedded import attendee
from organizer.api.resources.embedded.attendee import *
from organizer.api.resources.embedded import calendar_acl
from organizer.api.resources.embedded.calendar_acl import *
from organizer.api.resources.embedded import event_date_time
from organizer.api.resources.embedded.event_date_time import *
from organizer.api.resources.embedded import reminder
from organizer.api.resources.embedded.reminder import *


__all__ = (
    attendee.__all__ +
    calendar_acl.__all__ +
    event_date_time.__all__ +
    reminder.__all__
)
