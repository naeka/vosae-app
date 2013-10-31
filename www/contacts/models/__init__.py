# -*- coding:Utf-8 -*-

from mongoengine import signals

from contacts.models import embedded
from contacts.models.embedded import *

from contacts.models import entity
from contacts.models.entity import *
from contacts.models import contact
from contacts.models.contact import *
from contacts.models import organization
from contacts.models.organization import *
from contacts.models import contact_group
from contacts.models.contact_group import *


__all__ = (
    embedded.__all__ +
    entity.__all__ +
    contact.__all__ +
    organization.__all__ +
    contact_group.__all__
)


"""
SIGNALS
"""


signals.post_save.connect(Entity.post_save, sender=Contact)
signals.post_save.connect(Entity.post_save, sender=Organization)

signals.post_delete.connect(Entity.post_delete, sender=Contact)
signals.post_delete.connect(Entity.post_delete, sender=Organization)
