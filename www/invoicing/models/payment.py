# -*- coding:Utf-8 -*-

from mongoengine import Document, fields
from django.utils.timezone import now
import decimal

from core.fields import DateField
from invoicing import PAYMENT_TYPES, currency_format
from invoicing.exceptions import (
    InvalidPaymentAmount,
)


__all__ = (
    'Payment',
    'InvoicePayment',
    'DownPaymentInvoicePayment',
)


class Payment(Document):

    """
    A payment, representing money flows within the company.

    Amount can be negative (debit) or positive (credit).
    """
    TYPES = PAYMENT_TYPES

    tenant = fields.ReferenceField("Tenant", required=True)
    issuer = fields.ReferenceField("VosaeUser", required=True)
    issued_at = fields.DateTimeField(required=True, default=now)
    amount = fields.DecimalField(required=True)
    currency = fields.ReferenceField("Currency", required=True)
    type = fields.StringField(required=True, choices=TYPES, default="CHECK")
    date = DateField(required=True)
    note = fields.StringField(max_length=512)

    meta = {
        "allow_inheritance": True
    }

    def __unicode__(self):
        if self.date and self.amount and self.currency:
            return u'%s: %s' % (self.date, currency_format(self.amount, self.currency.symbol, True))
        return '%s object' % self.__class__.__name__

    @classmethod
    def pre_save(self, sender, document, **kwargs):
        """
        Pre save hook handler

        Validates payment amount
        """
        # If amount set from float (not from string), the rounding is only done on init or on save
        # So, we round here to prevent incorrect comparison
        document.amount = document.amount.quantize(decimal.Decimal('.00'), decimal.ROUND_HALF_UP)
        if document.amount < 0 or document.amount > document.related_to.balance:
            raise InvalidPaymentAmount()

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        """
        Post save hook handler

        - Associates payment to related document
        - Creates a payment statistic entry
        """
        from vosae_statistics.models import PaymentStatistics
        if created:
            document.related_to.payments.append(document)
        document.related_to.save()

        # XXX: Should save organization/contact/address
        payment_statistic = PaymentStatistics(
            tenant=document.tenant,
            date=document.date,
            amount=document.amount,
            payment=document
        ).save()

    @classmethod
    def post_delete(self, sender, document, **kwargs):
        """
        Post delete hook handler

        Removes payment from related document
        """
        document.related_to.payments.pop(document)
        document.related_to.save()


class InvoicePayment(Payment):

    """Payment related to an :class:`~invoicing.models.Invoice`"""
    related_to = fields.ReferenceField("Invoice", required=True, dbref=False)


class DownPaymentInvoicePayment(Payment):

    """Payment related to an :class:`~invoicing.models.DownPaymentInvoice`"""
    related_to = fields.ReferenceField("DownPaymentInvoice", required=True, dbref=False)
