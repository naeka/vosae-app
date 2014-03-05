# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import floatformat
from mongoengine import fields
from decimal import Decimal, ROUND_HALF_UP

from vosae_utils import SearchDocumentMixin
from pyes import mappings as search_mappings

from invoicing.exceptions import InvalidInvoiceBaseState
from invoicing.models.invoice import Invoice


__all__ = ('DownPaymentInvoice',)


class DownPaymentInvoice(Invoice, SearchDocumentMixin):

    """Base class for all down payments invoices (either payable or receivable)."""
    ITEM_REFERENCE = _("DOWN-PAYMENT")
    percentage = fields.DecimalField(required=True)
    tax_applied = fields.ReferenceField("Tax", required=True)

    class Meta():
        document_type = 'downpaymentinvoice'
        document_boost = 1
        fields = [
            search_mappings.StringField(name="reference", boost=document_boost * 3.0, index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="related_quotation_reference", boost=document_boost * 1.5, index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="contact", index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="organization", index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.DateField(name="invoicing_date", index="analyzed", term_vector="with_positions_offsets", include_in_all=False),
            search_mappings.StringField(name="state", index="not_analyzed", term_vector="with_positions_offsets", include_in_all=False),
        ]

    class InvalidState(InvalidInvoiceBaseState):

        def __init__(self, **kwargs):
            super(DownPaymentInvoice.InvalidState, self).__init__(**kwargs)
            self.message = 'Invalid down-payment state'

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        """
        Post save hook handler

        If created, append the down-payment invoice to the group.
        """
        if created:
            document.group.down_payment_invoices.append(document)
            document.group.save()

        # Calling *Invoice* parent
        super(Invoice, document).post_save(sender, document, created, **kwargs)

    def is_modifiable(self):
        """
        A :class:`~invoicing.models.DownPaymentInvoice` is automatically generated
        and can't be modified at any time.
        """
        return False

    def is_invoice(self):
        """A DownPaymentInvoice inherits from Invoice but types should be explicitely checked for both"""
        return False

    def is_down_payment_invoice(self):
        return True

    def manage_amounts(self):
        """
        Set total and amount of the :class:`~invoicing.models.DownPaymentInvoice`.

        Includes :class:`~invoicing.models.InvoiceItem`\ 's unit prices and taxes.
        """
        super(Invoice, self).manage_amounts()
        self.balance = self.amount - self.paid

    def get_item_description(self):
        """
        Returns a tuple composed of a dummy translation of the description and its context
        """
        _ = lambda s: s
        if self.related_to.is_quotation():
            return (_("%(percentage)s%% down-payment on quotation %(reference)s"), {
                'percentage': floatformat(float(self.percentage * 100), -2),
                'reference': self.related_to.reference
            })
        elif self.related_to.is_purchase_order():
            return (_("%(percentage)s%% down-payment on purchase order %(reference)s"), {
                'percentage': floatformat(float(self.percentage * 100), -2),
                'reference': self.related_to.reference
            })
        return (_("%(percentage)s%% down-payment"), {
            'percentage': floatformat(float(self.percentage * 100), -2),
        })
