# -*- coding:Utf-8 -*-

from contacts.models.embedded import address
from contacts.models.embedded.address import *
from contacts.models.embedded import email
from contacts.models.embedded.email import *
from contacts.models.embedded import phone
from contacts.models.embedded.phone import *


__all__ = (
    address.__all__ +
    email.__all__ +
    phone.__all__
)
