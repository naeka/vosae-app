# -*- coding: utf-8 -*-

from blinker import Namespace

__all__ = (
    'post_make_purchase_order',
    'post_make_invoice',
    'post_make_down_payment_invoice',
    'post_update_invoicebase',
    'post_register_invoice',
    'post_cancel_invoice',
    'post_client_changed_invoice_state',
)


_signals = Namespace()


post_make_purchase_order = _signals.signal('post_make_purchase_order')
post_make_invoice = _signals.signal('post_make_invoice')
post_make_down_payment_invoice = _signals.signal('post_make_down_payment_invoice')
post_update_invoicebase = _signals.signal('post_update_invoicebase')
post_register_invoice = _signals.signal('post_register_invoice')
post_cancel_invoice = _signals.signal('post_cancel_invoice')
post_client_changed_invoice_state = _signals.signal('post_client_changed_invoice_state')
