# -*- coding:Utf-8 -*-

from invoicing.api.resources.embedded import exchange_rate
from invoicing.api.resources.embedded.exchange_rate import *
from invoicing.api.resources.embedded import invoice_history_entries
from invoicing.api.resources.embedded.invoice_history_entries import *
from invoicing.api.resources.embedded import invoice_item
from invoicing.api.resources.embedded.invoice_item import *
from invoicing.api.resources.embedded import invoice_note
from invoicing.api.resources.embedded.invoice_note import *
from invoicing.api.resources.embedded import invoice_revision
from invoicing.api.resources.embedded.invoice_revision import *
from invoicing.api.resources.embedded import snapshot_currency
from invoicing.api.resources.embedded.snapshot_currency import *


__all__ = (
    exchange_rate.__all__ +
    invoice_history_entries.__all__ +
    invoice_item.__all__ +
    invoice_note.__all__ +
    invoice_revision.__all__ +
    snapshot_currency.__all__
)
