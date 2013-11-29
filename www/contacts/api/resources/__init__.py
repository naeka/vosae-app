# -*- coding:Utf-8 -*-

from core.api import signals

from contacts.api.resources import embedded
from contacts.api.resources.embedded import *

from contacts.api.resources import entity
from contacts.api.resources.entity import *
from contacts.api.resources import contact
from contacts.api.resources.contact import *
from contacts.api.resources import organization
from contacts.api.resources.organization import *


__all__ = (
    embedded.__all__ +
    contact.__all__ +
    organization.__all__
)


"""
SIGNALS
"""

signals.post_save.connect(EntityResource.post_save, sender=ContactResource)
signals.post_save.connect(EntityResource.post_save, sender=OrganizationResource)
