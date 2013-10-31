# -*- coding:Utf-8 -*-

from notification.api.resources import contacts_notifications
from notification.api.resources.contacts_notifications import *
from notification.api.resources import invoicing_notifications
from notification.api.resources.invoicing_notifications import *
from notification.api.resources import notification_resource
from notification.api.resources.notification_resource import *


__all__ = (
    contacts_notifications.__all__ +
    invoicing_notifications.__all__ +
    notification_resource.__all__
)
