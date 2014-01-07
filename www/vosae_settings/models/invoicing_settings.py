# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from decimal import Decimal

from mongoengine import fields, EmbeddedDocument
from invoicing import (
    TAXES_APPLICATION,
    PAYMENT_TYPES,
    PAYMENT_CONDITIONS
)


"""
INVOICING SETTINGS
All settings related to the invoicing app.
"""


__all__ = (
    'VosaeInvoicingMixin',
    'InvoicingSettings'
)


class InvoicingNumberingSettings(EmbeddedDocument):

    """A wrapper to Invoicing's module numbering settings."""
    SCHEMES = (
        ("DN", _("Date, Number")),
        ("N",  _("Number"))
    )
    DATE_FORMATS = (
        ("Ymd", _("YYYYMMDD")),
        ("dmY", _("DDMMYYYY")),
        ("ymd", _("YYMMDD")),
        ("dmy", _("DDMMYY")),
        ("Ym", _("YYYYMM")),
        ("mY", _("MMYYYY")),
        ("ym", _("YYMM")),
        ("my", _("MMYY")),
        ("Y", _("YYYY")),
        ("y", _("YY"))
    )
    DATE_STRFTIME_FORMATS = {
        "Ymd": "%Y%m%d",
        "dmY": "%d%m%Y",
        "ymd": "%y%m%d",
        "dmy": "%d%m%y",
        "Ym": "%Y%m",
        "mY": "%m%Y",
        "ym": "%y%m",
        "my": "%m%y",
        "Y": "%Y",
        "y": "%y"
    }
    SEPARATORS = (
        ("", _("No separator")),
        ("-", _("- (dash)")),
        ("_", _("_ (underscore)")),
        (".", _(". (dot)")),
        (":", _(": (colon)")),
        ("::", _(":: (bi-colon)")),
        ("/", _("/ (slash)")),
        ("#", _("# (sharp)"))
    )

    scheme = fields.StringField(required=True, choices=SCHEMES, default="DN")
    separator = fields.StringField(required=True, choices=SEPARATORS, default="-")
    date_format = fields.StringField(required=True, choices=DATE_FORMATS, default="Ym")
    all_time_quotation_counter = fields.IntField(required=True, min_value=1, default=1)
    all_time_purchase_order_counter = fields.IntField(required=True, min_value=1, default=1)
    all_time_invoice_counter = fields.IntField(required=True, min_value=1, default=1)
    all_time_credit_note_counter = fields.IntField(required=True, min_value=1, default=1)
    fy_quotation_counter = fields.IntField(required=True, min_value=1, default=1)
    fy_purchase_order_counter = fields.IntField(required=True, min_value=1, default=1)
    fy_invoice_counter = fields.IntField(required=True, min_value=1, default=1)
    fy_credit_note_counter = fields.IntField(required=True, min_value=1, default=1)
    fy_reset = fields.BooleanField(required=True, default=True)


class InvoicingSettings(EmbeddedDocument):

    """A wrapper to Invoicing's module settings."""
    TAXES_APPLICATION = TAXES_APPLICATION
    PAYMENT_TYPES = PAYMENT_TYPES
    PAYMENT_CONDITIONS = PAYMENT_CONDITIONS

    supported_currencies = fields.ListField(fields.ReferenceField("Currency"))
    default_currency = fields.ReferenceField("Currency", required=True)
    fy_start_month = fields.IntField(required=True, default=0, min_value=0, max_value=11)
    inv_taxes_application = fields.StringField(required=True, choices=TAXES_APPLICATION, default="EXCLUSIVE")
    quotation_validity = fields.IntField(required=True, default=30)
    payment_conditions = fields.StringField(required=True, choices=PAYMENT_CONDITIONS, default="CASH")
    custom_payment_conditions = fields.StringField()
    accepted_payment_types = fields.ListField(fields.StringField(choices=PAYMENT_TYPES), required=True, default=lambda: ["CHECK", "CASH", "CREDIT_CARD", "TRANSFER"])
    late_fee_rate = fields.DecimalField()
    down_payment_percent = fields.DecimalField(required=True, default=lambda: Decimal("0"))
    automatic_reminders = fields.BooleanField(required=True, default=False)
    automatic_reminders_text = fields.StringField(max_length=1024)
    automatic_reminders_send_copy = fields.BooleanField(required=True, default=True)
    numbering = fields.EmbeddedDocumentField("InvoicingNumberingSettings", required=True, default=lambda: InvoicingNumberingSettings())


class VosaeInvoicingMixin(object):

    """
    An Invoicing settings mixin allowing to perform quick operation.

    *All settings methods must be defined in documents containers. Data remains
    in embedded (nested or not) documents.*

    """
    @classmethod
    def pre_save(self, sender, document, **kwargs):
        if document.invoicing.default_currency:
            if document.invoicing.default_currency not in document.invoicing.supported_currencies:
                document.invoicing.supported_currencies.append(document.invoicing.default_currency)

    def get_quotation_counter(self):
        """
        Returns the appropriate :class:`~invoicing.models.Quotation` counter,
        based on date scheme and FY reset.
        """
        self.reload()
        if self.invoicing.numbering.fy_reset:
            return self.invoicing.numbering.fy_quotation_counter
        return self.invoicing.numbering.all_time_quotation_counter

    def get_purchase_order_counter(self):
        """
        Returns the appropriate :class:`~invoicing.models.PurchaseOrder` counter,
        based on date scheme and FY reset.
        """
        self.reload()
        if self.invoicing.numbering.fy_reset:
            return self.invoicing.numbering.fy_purchase_order_counter
        return self.invoicing.numbering.all_time_purchase_order_counter

    def get_invoice_counter(self):
        """
        Returns the appropriate :class:`~invoicing.models.Invoice` counter,
        based on date scheme and FY reset.
        """
        self.reload()
        if self.invoicing.numbering.fy_reset:
            return self.invoicing.numbering.fy_invoice_counter
        return self.invoicing.numbering.all_time_invoice_counter

    def get_credit_note_counter(self):
        """
        Returns the appropriate :class:`~invoicing.models.CreditNote` counter,
        based on date scheme and FY reset.
        """
        self.reload()
        if self.invoicing.numbering.fy_reset:
            return self.invoicing.numbering.fy_credit_note_counter
        return self.invoicing.numbering.all_time_credit_note_counter

    def set_quotation_counter(self, value, force=False):
        """
        Set the given value to the appropriate :class:`~invoicing.models.Quotation` counter,
        based on date scheme and FY reset.

        *This performs an update on the database. Does not reload settings.*
        """
        if not isinstance(value, (int, long)):
            raise Exception("Counter value must be integer or long")
        if self.get_quotation_counter() > value and not force:
            raise Exception("Counter value can only be incremented")

        if self.invoicing.numbering.fy_reset:
            self.update(set__invoicing__numbering__fy_quotation_counter=value)
            self.invoicing.numbering.fy_quotation_counter = value
        else:
            self.update(set__invoicing__numbering__all_time_quotation_counter=value)
            self.invoicing.numbering.all_time_quotation_counter = value

    def set_purchase_order_counter(self, value, force=False):
        """
        Set the given value to the appropriate :class:`~invoicing.models.PurchaseOrder` counter,
        based on date scheme and FY reset.

        *This performs an update on the database. Does not reload settings.*
        """
        if not isinstance(value, (int, long)):
            raise Exception("Counter value must be integer or long")
        if self.get_purchase_order_counter() > value and not force:
            raise Exception("Counter value can only be incremented")

        if self.invoicing.numbering.fy_reset:
            self.update(set__invoicing__numbering__fy_purchase_order_counter=value)
            self.invoicing.numbering.fy_purchase_order_counter = value
        else:
            self.update(set__invoicing__numbering__all_time_purchase_order_counter=value)
            self.invoicing.numbering.all_time_purchase_order_counter = value

    def set_invoice_counter(self, value, force=False):
        """
        Set the given value to the appropriate :class:`~invoicing.models.Invoice` counter,
        based on date scheme and FY reset.

        *This performs an update on the database. Does not reload settings.*
        """
        if not isinstance(value, (int, long)):
            raise Exception("Counter value must be integer or long")
        if self.get_invoice_counter() > value and not force:
            raise Exception("Counter value can only be incremented")

        if self.invoicing.numbering.fy_reset:
            self.update(set__invoicing__numbering__fy_invoice_counter=value)
            self.invoicing.numbering.fy_invoice_counter = value
        else:
            self.update(set__invoicing__numbering__all_time_invoice_counter=value)
            self.invoicing.numbering.all_time_invoice_counter = value

    def set_credit_note_counter(self, value, force=False):
        """
        Set the given value to the appropriate :class:`~invoicing.models.CreditNote` counter,
        based on date scheme and FY reset.

        *This performs an update on the database. Does not reload settings.*
        """
        if not isinstance(value, (int, long)):
            raise Exception("Counter value must be integer or long")
        if self.get_credit_note_counter() > value and not force:
            raise Exception("Counter value can only be incremented")

        if self.invoicing.numbering.fy_reset:
            self.update(set__invoicing__numbering__fy_credit_note_counter=value)
            self.invoicing.numbering.fy_credit_note_counter = value
        else:
            self.update(set__invoicing__numbering__all_time_credit_note_counter=value)
            self.invoicing.numbering.all_time_credit_note_counter = value

    def increment_quotation_counter(self):
        """
        Increments the appropriate :class:`~invoicing.models.Quotation` counter,
        based on date scheme and FY reset.

        *This performs an update on the database. Does not reload settings.*
        """
        if self.invoicing.numbering.fy_reset:
            self.update(inc__invoicing__numbering__fy_quotation_counter=1)
            self.reload()
        else:
            self.update(inc__invoicing__numbering__all_time_quotation_counter=1)
            self.reload()

    def increment_purchase_order_counter(self):
        """
        Increments the appropriate :class:`~invoicing.models.PurchaseOrder` counter,
        based on date scheme and FY reset.

        *This performs an update on the database. Does not reload settings.*
        """
        if self.invoicing.numbering.fy_reset:
            self.update(inc__invoicing__numbering__fy_purchase_order_counter=1)
            self.reload()
        else:
            self.update(inc__invoicing__numbering__all_time_purchase_order_counter=1)
            self.reload()

    def increment_invoice_counter(self):
        """
        Increments the appropriate :class:`~invoicing.models.Invoice` counter,
        based on date scheme and FY reset.

        *This performs an update on the database. Does not reload settings.*
        """
        if self.invoicing.numbering.fy_reset:
            self.update(inc__invoicing__numbering__fy_invoice_counter=1)
            self.reload()
        else:
            self.update(inc__invoicing__numbering__all_time_invoice_counter=1)
            self.reload()

    def increment_credit_note_counter(self):
        """
        Increments the appropriate :class:`~invoicing.models.CreditNote` counter,
        based on date scheme and FY reset.

        *This performs an update on the database. Does not reload settings.*
        """
        if self.invoicing.numbering.fy_reset:
            self.update(inc__invoicing__numbering__fy_credit_note_counter=1)
            self.reload()
        else:
            self.update(inc__invoicing__numbering__all_time_credit_note_counter=1)
            self.reload()
