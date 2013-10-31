# -*- coding:Utf-8 -*-

from organizer.api.resources import embedded
from organizer.api.resources.embedded import *

from organizer.api.resources import calendar
from organizer.api.resources.calendar import *
from organizer.api.resources import calendar_list
from organizer.api.resources.calendar_list import *
from organizer.api.resources import event
from organizer.api.resources.event import *


__all__ = (
    embedded.__all__ +
    calendar.__all__ +
    calendar_list.__all__ +
    event.__all__
)
