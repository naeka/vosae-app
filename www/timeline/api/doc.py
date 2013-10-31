# -*- coding:Utf-8 -*-

HELP_TEXT = {
    'timeline_entry': {
        'module': 'Module related to the timeline',
        'datetime': 'Datetime of the timeline entry',
        'issuer': 'User which have done an action resulting in the timeline entry creation',
    },
    'entity_saved': {
        'created': 'Indicates if the contact/organization has been created or updated',
        'contact': 'The contact saved',
        'organization': 'The organization saved',
    },
    'invoicebase_saved': {
        'created': 'Indicates if the quotation/invoice/credit note has been created or updated',
        'quotation': 'The quotation saved',
        'invoice': 'The invoice saved',
        'down_payment_invoice': 'The down-payment invoice saved',
        'credit_note': 'The credit note saved',
        'customer_display': 'Customer\'s representation',
        'contact': 'The related contact',
        'organization': 'The related organization',
        'has_temporary_reference': 'Invoice/Down-payment invoice temporary reference status',
    },
    'invoicebase_changed_state': {
        'quotation': 'Quotation whose state has changed',
        'invoice': 'Invoice whose state has changed',
        'down_payment_invoice': 'Down-payment invoice whose state has changed',
        'credit_note': 'Credit note whose state has changed',
        'previous_state': 'Previous state of the quotation/invoice/credit note',
        'new_state': 'New state applied to the quotation/invoice/credit note',
    },
    'quotation_make_invoice': {
        'quotation': 'The quotation from which the invoice has been made',
        'invoice': 'The generated invoice',
        'down_payment_invoice': 'The generated down-payment invoice',
        'customer_display': 'Customer\'s representation',
        'has_temporary_reference': 'Invoice/Down-payment invoice temporary reference status',
    },
    'invoice_cancelled': {
        'invoice': 'The cancelled invoice',
        'down_payment_invoice': 'The cancelled down-payment invoice',
        'credit_note': 'The generated credit note',
    },
}
