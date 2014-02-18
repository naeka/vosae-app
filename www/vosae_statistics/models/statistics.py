# -*- coding:Utf-8 -*-

from mongoengine import DynamicDocument, fields, CASCADE, NULLIFY
import inflection
import re

from core.fields import DateField
from invoicing import ACCOUNT_TYPES
from realtime.utils import emit_to_channel


__all__ = (
    'Statistics',
    'InvoiceStatistics',
    'DownPaymentInvoiceStatistics',
    'CreditNoteStatistics',
    'PaymentStatistics'
)


"""
Mixins
"""


class ContactsMixin(object):
    organization = fields.ReferenceField("Organization", reverse_delete_rule=NULLIFY)
    contact = fields.ReferenceField("Contact", reverse_delete_rule=NULLIFY)


class LocationMixin(object):
    location = fields.EmbeddedDocumentField("Address")


class AmountMixin(object):
    amount = fields.DecimalField()


"""
Bases
"""


class Statistics(DynamicDocument):
    USED_BY = []
    _type = None

    tenant = fields.ReferenceField("Tenant", required=True)
    type = fields.StringField(required=True)
    date = DateField(required=True)

    meta = {
        "indexes": ["tenant", "date"],
        "ordering": ["-date"],
        "allow_inheritance": True
    }

    @classmethod
    def _get_type(cls):
        if not cls._type:
            cls._type = inflection.underscore(re.sub('Statistics$', '', cls.__name__))
        return cls._type

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        """
        Post save hook handler

        Triggers a "statistics-update" message through the realtime service
        """
        from core.models import VosaeUser
        if document.USED_BY:
            for user_id in VosaeUser.objects.filter(tenant=document.tenant, state='ACTIVE').values_list('id'):
                emit_to_channel(u'private-user-{0}'.format(unicode(user_id)), u'statistics-update', {
                    u'statistics': document.USED_BY
                })

    def save(self, *args, **kwargs):
        self.type = self._get_type()
        super(Statistics, self).save(*args, **kwargs)


class InvoiceBaseStatistics(Statistics, ContactsMixin, LocationMixin, AmountMixin):
    USED_BY = ['invoicingFyFlowStatistics']
    account_type = fields.StringField(required=True, choices=ACCOUNT_TYPES)

    meta = {
        "indexes": ["organization", "contact", "amount", "account_type"],
        "allow_inheritance": True
    }


"""
Statistic documents
"""


class InvoiceStatistics(InvoiceBaseStatistics):
    invoice = fields.ReferenceField("Invoice", required=True, reverse_delete_rule=CASCADE)


class DownPaymentInvoiceStatistics(InvoiceBaseStatistics):
    down_payment_invoice = fields.ReferenceField("DownPaymentInvoice", required=True, reverse_delete_rule=CASCADE)


class CreditNoteStatistics(InvoiceBaseStatistics):
    credit_note = fields.ReferenceField("CreditNote", required=True, reverse_delete_rule=CASCADE)


class PaymentStatistics(Statistics, ContactsMixin, LocationMixin, AmountMixin):
    payment = fields.ReferenceField("Payment", required=True, reverse_delete_rule=CASCADE)

    meta = {
        "indexes": ["organization", "contact", "amount"]
    }
