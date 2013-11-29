# -*- coding:Utf-8 -*-

from mongoengine import signals
from notification.models.base import Notification

from notification.models.invoicing_notifications import invoicebase_saved
from notification.models.invoicing_notifications.invoicebase_saved import *
from notification.models.invoicing_notifications import invoicebase_changed_state
from notification.models.invoicing_notifications.invoicebase_changed_state import *
from notification.models.invoicing_notifications import make_purchase_order
from notification.models.invoicing_notifications.make_purchase_order import *
from notification.models.invoicing_notifications import make_invoice
from notification.models.invoicing_notifications.make_invoice import *
from notification.models.invoicing_notifications import invoice_cancelled
from notification.models.invoicing_notifications.invoice_cancelled import *


__all__ = (
	invoicebase_saved.__all__ +
	invoicebase_changed_state.__all__ +
    make_purchase_order.__all__ +
    make_invoice.__all__ +
	invoice_cancelled.__all__
)


"""
SIGNALS
"""


signals.post_save.connect(Notification.post_save, sender=QuotationSaved)
signals.post_save.connect(Notification.post_save, sender=QuotationChangedState)
signals.post_save.connect(Notification.post_save, sender=QuotationMakePurchaseOrder)
signals.post_save.connect(Notification.post_save, sender=QuotationMakeInvoice)
signals.post_save.connect(Notification.post_save, sender=QuotationMakeDownPaymentInvoice)
signals.post_save.connect(Notification.post_save, sender=InvoiceSaved)
signals.post_save.connect(Notification.post_save, sender=InvoiceChangedState)
signals.post_save.connect(Notification.post_save, sender=InvoiceCancelled)
signals.post_save.connect(Notification.post_save, sender=DownPaymentInvoiceSaved)
signals.post_save.connect(Notification.post_save, sender=DownPaymentInvoiceChangedState)
signals.post_save.connect(Notification.post_save, sender=DownPaymentInvoiceCancelled)
signals.post_save.connect(Notification.post_save, sender=CreditNoteSaved)
signals.post_save.connect(Notification.post_save, sender=CreditNoteChangedState)
