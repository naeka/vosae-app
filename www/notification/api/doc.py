# -*- coding:Utf-8 -*-

HELP_TEXT = {
    'notification_base': {
        'sent_at': 'Notification\'s sent datetime',
        'recipient': 'Notification\'s recipient',
        'read': 'Notification\'s read status',
    },
    'entity_saved': {
        'contact': 'Contact saved',
        'organization': 'Organization saved',
    },
    'invoicebase_saved': {
        'quotation': 'Quotation saved',
        'purchase_order': 'Purchase order saved',
        'invoice': 'Invoice saved',
        'down_payment_invoice': 'Down-payment invoice saved',
        'credit_note': 'Credit note saved',
        'customer_display': 'Customer\'s representation',
        'has_temporary_reference': 'Invoice/Down-payment invoice temporary reference status',
    },
    'invoicebase_changed_state': {
        'quotation': 'Quotation whose state has changed',
        'purchase_order': 'Purchase order whose state has changed',
        'invoice': 'Invoice whose state has changed',
        'down_payment_invoice': 'Down-payment invoice whose state has changed',
        'credit_note': 'Credit note whose state has changed',
    },
    'quotation_make_purchase_order': {
        'quotation': 'The quotation from which the purchase order has been made',
        'purchase_order': 'The generated purchase order',
    },
    'quotation_make_invoice': {
        'quotation': 'The quotation from which the invoice has been made',
        'invoice': 'The generated invoice',
        'down_payment_invoice': 'The generated down-payment invoice',
    },
    'purchase_order_make_invoice': {
        'purchase_order': 'The purchase order from which the invoice has been made',
        'invoice': 'The generated invoice',
        'down_payment_invoice': 'The generated down-payment invoice',
    },
    'invoice_cancelled': {
        'invoice': 'The cancelled invoice',
        'down_payment_invoice': 'The cancelled down-payment invoice',
        'credit_note': 'The generated credit note',
    },
    'event_reminder': {
        'occurs_at': 'The datetime when the event starts',
        'summary': 'The summary of the event',
        'vosae_event': 'The related vosae event',
    },
}
