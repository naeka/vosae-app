# -*- coding:Utf-8 -*-

from notification.models.base import Notification


__all__ = (
    'InvoicingNotification',
)


class InvoicingNotification(Notification):

    meta = {
        "allow_inheritance": True
    }

    # Signals handler goes here
