# -*- coding:Utf-8 -*-

from django.utils.translation import pgettext_lazy
from django.utils.formats import get_format, number_format
from dateutil.relativedelta import *
import datetime
import re

from vosae_utils import StateList


INVOICEBASE_DERIVED = (
    'Quotation',
    'PurchaseOrder',
    'Invoice',
    'DownPaymentInvoice',
    'CreditNote'
)

QUOTATION_STATES = StateList((
    ("DRAFT", pgettext_lazy("quotation state", "Draft")),
    ("AWAITING_APPROVAL", pgettext_lazy("quotation state", "Awaiting approval")),
    ("APPROVED", pgettext_lazy("quotation state", "Approved")),
    ("REFUSED", pgettext_lazy("quotation state", "Refused")),
    ("EXPIRED", pgettext_lazy("quotation state", "Expired")),
    ("INVOICED", pgettext_lazy("quotation state", "Invoiced"))
))

PURCHASE_ORDER_STATES = StateList((
    ("DRAFT", pgettext_lazy("purchase order state", "Draft")),
    ("AWAITING_APPROVAL", pgettext_lazy("purchase order state", "Awaiting approval")),
    ("APPROVED", pgettext_lazy("purchase order state", "Approved")),
    ("REFUSED", pgettext_lazy("purchase order state", "Refused")),
    ("INVOICED", pgettext_lazy("purchase order state", "Invoiced"))
))

DELIVERY_ORDER_STATES = StateList((
    ("DRAFT", pgettext_lazy("delivery order state", "Draft")),
    ("REGISTERED", pgettext_lazy("delivery order state", "Registered")),
    ("DELIVERED", pgettext_lazy("delivery order state", "Delivered")),
    ("REFUSED", pgettext_lazy("delivery order state", "Refused")),
    ("INVOICED", pgettext_lazy("delivery order state", "Invoiced"))
))

INVOICE_STATES = StateList((
    ("DRAFT", pgettext_lazy("invoice state", "Draft")),
    ("REGISTERED", pgettext_lazy("invoice state", "Registered")),
    ("OVERDUE", pgettext_lazy("invoice state", "Overdue")),
    ("PART_PAID", pgettext_lazy("invoice state", "Part paid")),
    ("PAID", pgettext_lazy("invoice state", "Paid")),
    ("CANCELLED", pgettext_lazy("invoice state", "Cancelled"))
))

CREDIT_NOTE_STATES = StateList((
    ("REGISTERED", pgettext_lazy("credit note state", "Registered")),
    ("SENT", pgettext_lazy("credit note state", "Sent")),
    ("PAID", pgettext_lazy("credit note state", "Paid"))
))

MARK_AS_STATES = (
    "AWAITING_APPROVAL",
    "APPROVED",
    "REFUSED",
    "DELIVERED",
    "REGISTERED",
    "SENT"
)

STATES_RESET_CACHED_DATA = (
    "REGISTERED",
)

HISTORY_STATES = MARK_AS_STATES + ('CANCELLED',)

CURRENCY_DISPLAY_SYMBOLS = {
    'AUD': u'$',
    'BRL': u'R$',
    'CAD': u'$',
    'CHF': u'Fr',
    'CNY': u'¥',
    'DKK': u'kr',
    'EGP': u'£',
    'EUR': u'€',
    'GBP': u'£',
    'HKD': u'$',
    'INR': u'₹',
    'JPY': u'¥',
    'MAD': u'د.م.',
    'MXN': u'$',
    'NOK': u'kr',
    'NZD': u'$',
    'RUB': u'р.',
    'SEK': u'kr',
    'TRY': u'£',
    'USD': u'$',
}

TAXES_APPLICATION = (
    ("EXCLUSIVE", pgettext_lazy("invoice taxes application", "Exclusive")),
    ("NOT_APPLICABLE", pgettext_lazy("invoice taxes application", "Not applicable"))
)

ACCOUNT_TYPES = (
    ("PAYABLE", pgettext_lazy("invoice type", "Payable invoice")),  # Supplier (money goes out)
    ("RECEIVABLE", pgettext_lazy("invoice type", "Receivable invoice"))  # Customer (money goes in)
)

PAYMENT_TYPES = (
    ("CASH", pgettext_lazy("payment type", "Cash")),
    ("CHECK", pgettext_lazy("payment type", "Check")),
    ("CREDIT_CARD", pgettext_lazy("payment type", "Credit card")),
    ("TRANSFER", pgettext_lazy("payment type", "Bank transfer")),
    ("OTHER", pgettext_lazy("payment type", "Other"))
)

PAYMENT_CONDITIONS = (
    ("CASH", pgettext_lazy("payment conditions", "Cash")),
    ("30D", pgettext_lazy("payment conditions", "30 days")),
    ("30D-EOM", pgettext_lazy("payment conditions", "30 days end of month")),
    ("30D-EOM-10", pgettext_lazy("payment conditions", "30 days end of month, the 10th")),
    ("45D", pgettext_lazy("payment conditions", "45 days")),
    ("45D-EOM", pgettext_lazy("payment conditions", "45 days end of month")),
    ("45D-EOM-10", pgettext_lazy("payment conditions", "45 days end of month, the 10th")),
    ("60D", pgettext_lazy("payment conditions", "60 days")),
    ("60D-EOM", pgettext_lazy("payment conditions", "60 days end of month")),
    ("60D-EOM-10", pgettext_lazy("payment conditions", "60 days end of month, the 10th")),
    ("CUSTOM", pgettext_lazy("payment conditions", "Custom")),
)

ITEM_TYPES = (
    ("PRODUCT", pgettext_lazy("item type", "Product")),
    ("SERVICE", pgettext_lazy("item type", "Service"))
)


def get_due_date(start_date, conditions):
    """
    Returns a date with an offset based on conditions like PAYMENT_CONDITIONS
    """
    if conditions == "CASH":
        return start_date
    elif conditions == "CUSTOM":
        return None
    else:
        found = re.findall(r"^([\d]{2})D", conditions)
        if not found:
            return None
        due_date = start_date + datetime.timedelta(days=int(found[0]))
        if 'EOM' in conditions:
            due_date = (due_date + relativedelta(months=1))
            if conditions.endswith('-EOM'):
                return due_date.replace(day=1) - datetime.timedelta(days=1)
            elif conditions.endswith('-EOM-10'):
                return due_date.replace(day=10)
        else:
            return due_date


def currency_format(value, symbol=None, iso4217=False, financial=False):
    """
    International currency format. Based on the current locale.
    """

    s = number_format(abs(round(value, 2)), 2)
    s = "<" + s + ">"  # "<" and ">" are markers if the sign must be inserted between symbol and value

    try:
        if symbol:
            smb = symbol
            if not iso4217 and symbol in CURRENCY_DISPLAY_SYMBOLS.keys():
                smb = CURRENCY_DISPLAY_SYMBOLS[symbol]
            precedes = get_format("N_CS_PRECEDES") if value < 0 else get_format("P_CS_PRECEDES")
            separated = (get_format("N_SEP_BY_SPACE") if value < 0 else get_format("P_SEP_BY_SPACE")) or iso4217
            if precedes:
                s = smb + (separated and " " or "") + s
            else:
                s = s + (separated and " " or "") + smb

        sign_pos = get_format("N_SIGN_POSN") if value < 0 else get_format("P_SIGN_POSN")
        sign = get_format("NEGATIVE_SIGN") if value < 0 else get_format("POSITIVE_SIGN")
        if sign_pos == 0 or (financial and value < 0):
            s = '(' + s + ')'
        elif sign_pos == 1:
            s = sign + s
        elif sign_pos == 2:
            s = s + sign
        elif sign_pos == 3:
            s = s.replace('<', sign)
        elif sign_pos == 4:
            s = s.replace('>', sign)
        else:
            # the default if nothing specified;
            # this should be the most fitting sign position
            s = sign + s
    except:
        pass
    return s.replace('<', '').replace('>', '')


"""
INVOICING PROCESSES:


QUOTATION:

                     ┌──────────────────────────┐
                     │          DRAFT           │
                     └──────────────────────────┘
                       │
                       │
                       ▼
┌─────────┐  auto    ┌──────────────────────────┐
│ EXPIRED │ ◀──────▶ │    AWAITING_APPROVAL     │ ◀┐
└─────────┘          └──────────────────────────┘  │
                       ▲                           │
                       │                           │
                       │                           │
                       ▼                           │
                     ┌──────────────────────────┐  │
                     │         REFUSED          │  │
                     └──────────────────────────┘  │
                       ▲                           │
                       │                           │
                       │                           │
                       ▼                           │
                     ┌──────────────────────────┐  │
             ┌────── │         APPROVED         │ ◀┘
             │       └──────────────────────────┘
             │         │
             │         │
             │         ▼
             │        CAN_MAKE_PURCHASE_ORDER
             │       ----------------------------──┐
             │                                     │
             │         │                           │
             │ auto    │                           │
             │         ▼                           │
             │        CAN_MAKE_DELIVERY_ORDERS     │
             │       ----------------------------  │ auto
             │                                     │
             │         │                           │
             │         │ auto                      │
             │         ▼                           │
             │       ┌──────────────────────────┐  │
             └─────▶ │         INVOICED         │ ◀┘
                     └──────────────────────────┘



PURCHASE ORDER:

                 ┌──────────────────────────┐
                 │          DRAFT           │
                 └──────────────────────────┘
                   │
                   │
                   ▼
┌─────────┐      ┌──────────────────────────┐
│ REFUSED │ ◀──▶ │    AWAITING_APPROVAL     │
└─────────┘      └──────────────────────────┘
                   ▲
                   │
                   │
                   ▼
                 ┌──────────────────────────┐
                 │         APPROVED         │ ─┐
                 └──────────────────────────┘  │
                   │                           │
                   │                           │
                   ▼                           │
                  CAN_MAKE_DELIVERY_ORDERS     │
                 ----------------------------  │ auto
                                               │
                   │                           │
                   │ auto                      │
                   ▼                           │
                 ┌──────────────────────────┐  │
                 │         INVOICED         │ ◀┘
                 └──────────────────────────┘



DELIVERY ORDER:

┌────────────┐
│   DRAFT    │
└────────────┘
  │
  │
  ▼
┌────────────┐
│ REGISTERED │ ─┐
└────────────┘  │
  │             │
  │             │
  ▼             │
┌────────────┐  │
│  REFUSED   │  │
└────────────┘  │
  │             │
  │             │
  ▼             │
┌────────────┐  │
│ DELIVERED  │ ◀┘
└────────────┘
  │
  │ auto
  ▼
┌────────────┐
│  INVOICED  │
└────────────┘



INVOICE:

         ┌────────────┐
         │   DRAFT    │
         └────────────┘
           │
           │
           ▼
         ┌────────────┐
  ┌───── │ REGISTERED │ ─┐
  │      └────────────┘  │
  │        │             │
  │        │ auto        │
  │        ▼             │
  │      ┌────────────┐  │
  │      │ PART_PAID  │ ─┼────────┐
  │      └────────────┘  │        │
  │        ▲             │        │
  │        │             │        │
  │ auto   │ auto        │ auto   │
  │        ▼             │        │
  │      ┌────────────┐  │        │
  │      │  OVERDUE   │ ◀┘        │
  │      └────────────┘           │
  │        │                      │
  │        │ auto                 │
  │        ▼                      │
  │      ┌────────────┐  auto     │
  └────▶ │    PAID    │ ◀─────────┘
         └────────────┘
           │
           │ auto
           ▼
         ┌────────────┐
         │ CANCELLED  │
         └────────────┘



CREDIT NOTE:

┌────────────┐
│ REGISTERED │ ─┐
└────────────┘  │
  │             │
  │             │
  ▼             │
┌────────────┐  │
│    SENT    │  │ auto
└────────────┘  │
  │             │
  │ auto        │
  ▼             │
┌────────────┐  │
│    PAID    │ ◀┘
└────────────┘

"""
