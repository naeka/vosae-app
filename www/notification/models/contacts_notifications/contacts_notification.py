# -*- coding:Utf-8 -*-

from notification.models.base import Notification


__all__ = (
    'ContactsNotification',
)


class ContactsNotification(Notification):

    meta = {
        "allow_inheritance": True
    }

    # Signals handler goes here
