# -*- coding:Utf-8 -*-

from mongoengine import signals, PULL, NULLIFY
from invoicing import signals as invoicing_signals

from invoicing.models import embedded
from invoicing.models.embedded import *

from invoicing.models import invoice_base
from invoicing.models.invoice_base import *
from invoicing.models import quotation
from invoicing.models.quotation import *
from invoicing.models import purchase_order
from invoicing.models.purchase_order import *
from invoicing.models import invoice
from invoicing.models.invoice import *
from invoicing.models import down_payment_invoice
from invoicing.models.down_payment_invoice import *
from invoicing.models import credit_note
from invoicing.models.credit_note import *
from invoicing.models import payment
from invoicing.models.payment import *
from invoicing.models import currency
from invoicing.models.currency import *
from invoicing.models import item
from invoicing.models.item import *
from invoicing.models import tax
from invoicing.models.tax import *


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
DELETE RULES
"""
DownPaymentInvoice.register_delete_rule(InvoiceBaseGroup, 'down_payment_invoices', PULL)
Invoice.register_delete_rule(InvoiceBaseGroup, 'invoice', NULLIFY)
Quotation.register_delete_rule(InvoiceBaseGroup, 'quotation', NULLIFY)
PurchaseOrder.register_delete_rule(InvoiceBaseGroup, 'purchase_order', NULLIFY)


"""
SIGNALS
"""


signals.pre_save.connect(Quotation.pre_save, sender=Quotation)
signals.pre_save.connect(PurchaseOrder.pre_save, sender=PurchaseOrder)
signals.pre_save.connect(Invoice.pre_save, sender=Invoice)
signals.pre_save.connect(DownPaymentInvoice.pre_save, sender=DownPaymentInvoice)
signals.pre_save.connect(CreditNote.pre_save, sender=CreditNote)
signals.pre_save.connect(Payment.pre_save, sender=InvoicePayment)
signals.pre_save.connect(Payment.pre_save, sender=DownPaymentInvoicePayment)

signals.post_save.connect(Quotation.post_save, sender=Quotation)
signals.post_save.connect(PurchaseOrder.post_save, sender=PurchaseOrder)
signals.post_save.connect(Invoice.post_save, sender=Invoice)
signals.post_save.connect(DownPaymentInvoice.post_save, sender=DownPaymentInvoice)
signals.post_save.connect(CreditNote.post_save, sender=CreditNote)
signals.post_save.connect(Item.post_save, sender=Item)
signals.post_save.connect(Payment.post_save, sender=InvoicePayment)
signals.post_save.connect(Payment.post_save, sender=DownPaymentInvoicePayment)

signals.post_delete.connect(Quotation.post_delete, sender=Quotation)
signals.post_delete.connect(PurchaseOrder.post_delete, sender=PurchaseOrder)
signals.post_delete.connect(Invoice.post_delete, sender=Invoice)
signals.post_delete.connect(DownPaymentInvoice.post_delete, sender=DownPaymentInvoice)
signals.post_delete.connect(CreditNote.post_delete, sender=CreditNote)
signals.post_delete.connect(Item.post_delete, sender=Item)
signals.post_delete.connect(Payment.post_delete, sender=InvoicePayment)
signals.post_delete.connect(Payment.post_delete, sender=DownPaymentInvoicePayment)

invoicing_signals.post_client_changed_invoice_state.connect(InvoiceBase.post_client_changed_invoice_state, sender=Quotation)
invoicing_signals.post_client_changed_invoice_state.connect(InvoiceBase.post_client_changed_invoice_state, sender=PurchaseOrder)
invoicing_signals.post_client_changed_invoice_state.connect(InvoiceBase.post_client_changed_invoice_state, sender=Invoice)
invoicing_signals.post_client_changed_invoice_state.connect(InvoiceBase.post_client_changed_invoice_state, sender=DownPaymentInvoice)
invoicing_signals.post_client_changed_invoice_state.connect(InvoiceBase.post_client_changed_invoice_state, sender=CreditNote)

invoicing_signals.post_make_purchase_order.connect(Quotation.post_make_purchase_order, sender=Quotation)

invoicing_signals.post_make_invoice.connect(Quotation.post_make_invoice, sender=Quotation)
invoicing_signals.post_make_invoice.connect(PurchaseOrder.post_make_invoice, sender=PurchaseOrder)
invoicing_signals.post_make_down_payment_invoice.connect(Quotation.post_make_down_payment_invoice, sender=Quotation)
invoicing_signals.post_make_down_payment_invoice.connect(PurchaseOrder.post_make_down_payment_invoice, sender=PurchaseOrder)

invoicing_signals.post_register_invoice.connect(Invoice.post_register_invoice, sender=Invoice)

invoicing_signals.post_cancel_invoice.connect(Invoice.post_cancel_invoice, sender=Invoice)
invoicing_signals.post_cancel_invoice.connect(Invoice.post_cancel_invoice, sender=DownPaymentInvoice)
