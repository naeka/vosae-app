# -*- coding:Utf-8 -*-

from core.api import signals

from invoicing.api.resources import embedded
from invoicing.api.resources.embedded import *

from invoicing.api.resources import invoice_base
from invoicing.api.resources.invoice_base import *
from invoicing.api.resources import quotation
from invoicing.api.resources.quotation import *
from invoicing.api.resources import purchase_order
from invoicing.api.resources.purchase_order import *
from invoicing.api.resources import invoice
from invoicing.api.resources.invoice import *
from invoicing.api.resources import down_payment_invoice
from invoicing.api.resources.down_payment_invoice import *
from invoicing.api.resources import credit_note
from invoicing.api.resources.credit_note import *
from invoicing.api.resources import payment
from invoicing.api.resources.payment import *
from invoicing.api.resources import currency
from invoicing.api.resources.currency import *
from invoicing.api.resources import item
from invoicing.api.resources.item import *
from invoicing.api.resources import tax
from invoicing.api.resources.tax import *


__all__ = (
    embedded.__all__ +
    invoice_base.__all__ +
    quotation.__all__ +
    purchase_order.__all__ +
    invoice.__all__ +
    down_payment_invoice.__all__ +
    credit_note.__all__ +
    payment.__all__ +
    currency.__all__ +
    item.__all__ +
    tax.__all__
)


"""
SIGNALS
"""

signals.post_save.connect(InvoiceBaseResource.post_save, sender=QuotationResource)
signals.post_save.connect(InvoiceBaseResource.post_save, sender=InvoiceResource)
signals.post_save.connect(InvoiceBaseResource.post_save, sender=DownPaymentInvoiceResource)
signals.post_save.connect(InvoiceBaseResource.post_save, sender=CreditNoteResource)
