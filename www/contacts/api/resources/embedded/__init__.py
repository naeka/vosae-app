# -*- coding:Utf-8 -*-

from contacts.api.resources.embedded import address
from contacts.api.resources.embedded.address import *
from contacts.api.resources.embedded import email
from contacts.api.resources.embedded.email import *
from contacts.api.resources.embedded import phone
from contacts.api.resources.embedded.phone import *


__all__ = (
    address.__all__ +
    email.__all__ +
    phone.__all__
)
