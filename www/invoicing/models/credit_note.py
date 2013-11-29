# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext_lazy as _, ugettext
from django.template.defaultfilters import floatformat
from mongoengine import fields
from decimal import Decimal, ROUND_HALF_UP
import datetime

from vosae_utils import SearchDocumentMixin
from pyes import mappings as search_mappings

from core.fields import MultipleReferencesField

from invoicing.exceptions import *
from invoicing.models.invoice_base import InvoiceBase
from invoicing import CREDIT_NOTE_STATES


__all__ = ('CreditNote',)


class CreditNote(InvoiceBase, SearchDocumentMixin):

    """Class for all credit notes (either payable or receivable)."""
    TYPE = "CREDIT_NOTE"
    RECORD_NAME = _("Credit note")
    STATES = CREDIT_NOTE_STATES

    state = fields.StringField(required=True, choices=STATES, default=STATES.REGISTERED)
    related_to = MultipleReferencesField(document_types=['DownPaymentInvoice', 'Invoice'])

    class Meta():
        document_type = 'creditnote'
        document_boost = 0.8
        fields = [
            search_mappings.StringField(name="reference", boost=document_boost * 3.0, index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="related_invoice_reference", boost=document_boost * 1.5, index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="contact", index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="organization", index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.DateField(name="invoicing_date_date", index="analyzed", term_vector="with_positions_offsets", include_in_all=False),
            search_mappings.StringField(name="state", index="not_analyzed", term_vector="with_positions_offsets", include_in_all=False),
        ]

    class InvalidState(InvalidInvoiceBaseState):

        def __init__(self, **kwargs):
            super(CreditNote.InvalidState, self).__init__(**kwargs)
            self.message = 'Invalid credit note state'

    def __init__(self, *args, **kwargs):
        from invoicing.models import InvoiceItem
        super(CreditNote, self).__init__(*args, **kwargs)
        if self.related_to and self.related_to.is_down_payment_invoice():
            credit_note_data = self.current_revision
            if credit_note_data and self.id:
                description = _("%(percentage)s%% down-payment")
                if self.related_to.related_to:  # Quotation | Purchase order (| Delivery order)
                    if self.related_to.related_to.is_quotation():
                        description = _("%(percentage)s%% down-payment on quotation %(reference)s")
                    elif self.related_to.related_to.is_purchase_order():
                        description = _("%(percentage)s%% down-payment on purchase order %(reference)s")                        
                credit_note_data.line_items.append(
                    InvoiceItem(
                        reference=self.related_to.ITEM_REFERENCE,
                        description=description % {
                            "percentage": floatformat(float(self.related_to.percentage * 100), -2),
                            "reference": self.related_to.related_to.reference
                        },
                        quantity=1,
                        unit_price=(self.amount / (Decimal('1.00') + self.related_to.tax_applied.rate)).quantize(Decimal('1.00'), ROUND_HALF_UP),
                        tax=self.related_to.tax_applied
                    )
                )

    def get_search_kwargs(self):
        kwargs = super(CreditNote, self).get_search_kwargs()
        if self.current_revision.invoicing_date:
            kwargs.update(invoicing_date=self.current_revision.invoicing_date)
        if self.related_to:
            kwargs.update(related_invoice_reference=self.related_to.reference)
        return kwargs

    @classmethod
    def pre_save(self, sender, document, **kwargs):
        """
        Pre save hook handler

        If credit note is in its creation process, affects the base type and the reference
        """
        # Calling parent
        super(CreditNote, document).pre_save(sender, document, **kwargs)

        if not document.is_created():
            document.base_type = document.TYPE
            document.reference = document.genere_reference(document.tenant.tenant_settings)

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        """
        Post save hook handler

        If created:
        - increments the appropriate :class:`~core.models.Tenant` quotations numbering counter.
        - append the credit note to the group
        """
        if created:
            document.tenant.tenant_settings.increment_credit_note_counter()
            document.group.credit_notes.append(document)
            document.group.save()

        # Calling parent
        super(CreditNote, document).post_save(sender, document, created, **kwargs)

    def genere_reference(self, tenant_settings):
        """
        Genere a unique reference for an :class:`~invoicing.models.CreditNote` object.

        Use the :class:`~core.models.Tenant` credit notes numbering counter.
        """
        if tenant_settings.invoicing.numbering.scheme == "DN":
            date = unicode(datetime.datetime.strftime(datetime.datetime.now(), tenant_settings.invoicing.numbering.DATE_STRFTIME_FORMATS[tenant_settings.invoicing.numbering.date_format]))
            counter = unicode("%0*d" % (5, tenant_settings.get_credit_note_counter()))
            elements = (date, counter)
        elif tenant_settings.invoicing.numbering.scheme == "N":
            counter = unicode("%0*d" % (5, tenant_settings.get_credit_note_counter()))
            elements = (counter,)
        else:
            return False
        return unicode(tenant_settings.invoicing.numbering.separator).join(elements)

    def set_total(self):
        """
        Set the total amount and adjusts it if the credit note is associated to an
        :class:`~invoicing.models.Invoice` and if there is any down payment.
        """
        super(CreditNote, self).set_total()
        if not self.related_to.is_down_payment_invoice():
            for down_payment_invoice in self.group.down_payment_invoices:
                self.amount += down_payment_invoice.amount

    def is_modifiable(self):
        """
        A :class:`~invoicing.models.CreditNote` is automatically generated and can't
        be modified at any time.
        """
        return False

    def is_issuable(self):
        """
        Determine if the :class:`~invoicing.models.CreditNote` could be sent. It is automatically
        generated and so could be sent at any time.
        """
        return True

    def is_credit_note(self):
        return True

    @staticmethod
    def full_export(tenant, start_date=None, end_date=None):
        def get_path(credit_note):
            return '{0}/{1}/{2}'.format(ugettext('Credit notes'), credit_note.current_revision.issue_date.strftime('%Y/%m'), credit_note.filename)

        def get_doc(credit_note):
            return credit_note.gen_pdf().getvalue()

        kwargs = {'tenant': tenant}
        if start_date:
            kwargs.update(current_revision__issue_date__gte=start_date)
        if end_date:
            kwargs.update(current_revision__issue_date__lt=end_date)
        queryset = CreditNote.objects.filter(**kwargs)
        return queryset, get_path, get_doc
