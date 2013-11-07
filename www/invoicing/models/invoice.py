# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext_lazy as _, pgettext, ugettext
from django.utils.timezone import now as datetime_now
from mongoengine import fields
from decimal import Decimal
import datetime
import uuid

from vosae_utils import SearchDocumentMixin
from pyes import mappings as search_mappings

from invoicing.exceptions import InvalidInvoiceBaseState, NotCancelableInvoice
from invoicing.models.invoice_base import InvoiceBase
from invoicing import signals as invoicing_signals
from invoicing import INVOICE_STATES
from invoicing.tasks import post_register_invoice_task, post_cancel_invoice_task


__all__ = ('Invoice',)


class Invoice(InvoiceBase, SearchDocumentMixin):

    """Invoices specific class."""
    TYPE = "INVOICE"
    RECORD_NAME = _("Invoice")
    STATES = INVOICE_STATES

    has_temporary_reference = fields.BooleanField(required=True, default=True)
    state = fields.StringField(required=True, choices=STATES, default=STATES.DRAFT)
    paid = fields.DecimalField(required=True, default=lambda: Decimal('0.00'))
    balance = fields.DecimalField(required=True)
    related_quotation = fields.ReferenceField("Quotation")
    payments = fields.ListField(fields.ReferenceField("Payment"))
    related_credit_note = fields.ReferenceField("CreditNote")

    meta = {
        "allow_inheritance": True
    }

    class Meta():
        document_type = 'invoice'
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
            super(Invoice.InvalidState, self).__init__(**kwargs)
            self.message = 'Invalid invoice state'

    def get_search_kwargs(self):
        kwargs = super(Invoice, self).get_search_kwargs()
        if self.current_revision.invoicing_date:
            kwargs.update(invoicing_date=self.current_revision.invoicing_date)
        if self.related_quotation:
            kwargs.update(related_quotation_reference=self.related_quotation.reference)
        return kwargs

    @classmethod
    def pre_save(self, sender, document, **kwargs):
        """
        Pre save hook handler

        - Manage payments and balance
        - Manage reference counters
        """
        # Calling parent
        super(Invoice, document).pre_save(sender, document, **kwargs)

        # Manage payments and balance
        document.manage_paid()

        # If the invoice already exists, it will be updated, otherwise it will be created.
        # When creating, it increments the appropriate :class:`~core.models.Tenant`
        # invoices numbering counter.
        if not document.is_created() and document.is_modifiable():
            document.base_type = document.TYPE
            document.has_temporary_reference = True
            temporary_ref = unicode(uuid.uuid4())
            document.reference = temporary_ref
        elif not document.is_modifiable() and (document.has_temporary_reference or not document.is_created()):
            document.base_type = document.TYPE
            document.has_temporary_reference = False
            document.reference = document.genere_reference(document.tenant.tenant_settings)
            document.tenant.tenant_settings.increment_invoice_counter()

    @classmethod
    def post_delete(self, sender, document, **kwargs):
        """
        Post delete hook handler

        - Update related quotation to remove linked invoices references
        """
        # Update related quotation
        if document.related_quotation:
            # Removes invoiced state
            document.related_quotation.remove_invoiced_state()
            # Reset related invoice
            document.related_quotation.related_invoice = None
            # Saves updates
            document.related_quotation.save()

        # Calling parent
        super(Invoice, document).post_delete(sender, document, **kwargs)

    @property
    def down_payments(self):
        """Property returning a list of down payment invoices (retrieved from related quotation)"""
        try:
            return self.related_quotation.down_payments
        except:
            return []

    @property
    def filename(self):
        """Return a filename based on invoice base type and reference"""
        if self.has_temporary_reference:
            reference = pgettext('invoice reference', 'not registered')
        else:
            reference = self.reference
        return u'{0} {1}.pdf'.format(self.RECORD_NAME, reference)

    def genere_reference(self, tenant_settings):
        """
        Genere a unique reference for an :class:`~invoicing.models.Invoice` object.

        Use the :class:`~core.models.Tenant` invoices numbering counter.
        """
        if tenant_settings.invoicing.numbering.scheme == "DN":
            date = unicode(datetime.datetime.strftime(datetime.datetime.now(), tenant_settings.invoicing.numbering.DATE_STRFTIME_FORMATS[tenant_settings.invoicing.numbering.date_format]))
            counter = unicode("%0*d" % (5, tenant_settings.get_invoice_counter()))
            elements = (date, counter)
        elif tenant_settings.invoicing.numbering.scheme == "N":
            counter = unicode("%0*d" % (5, tenant_settings.get_invoice_counter()))
            elements = (counter,)
        else:
            return False
        return unicode(tenant_settings.invoicing.numbering.separator).join(elements)

    def is_invoice(self):
        return True

    def is_modifiable(self):
        """True if the :class:`~invoicing.models.Invoice` is still in a modifiable state."""
        if self.state in (Invoice.STATES.DRAFT,):
            return True
        return False

    def is_deletable(self):
        """Determine if the :class:`~invoicing.models.Invoice` could be deleted."""
        if self.is_modifiable():
            return True
        return False

    def is_cancelable(self):
        """
        True if the :class:`~invoicing.models.Invoice` is in a cancelable state.
        When cancelable, a credit note could be created.
        """
        if self.state in (Invoice.STATES.REGISTERED, Invoice.STATES.OVERDUE, Invoice.STATES.PART_PAID, Invoice.STATES.PAID):
            return True
        return False

    def is_payable(self):
        """True if the :class:`~invoicing.models.Invoice` is in a payable state."""
        if self.state in (Invoice.STATES.REGISTERED, Invoice.STATES.OVERDUE, Invoice.STATES.PART_PAID):
            return True
        return False

    def is_issuable(self):
        """Determine if the :class:`~invoicing.models.Quotation` could be sent."""
        if self.state not in (Invoice.STATES.DRAFT, Invoice.STATES.CANCELLED):
            return True
        return False

    def is_paid(self):
        """True if the :class:`~invoicing.models.Invoice` is paid."""
        if self.state == Invoice.STATES.PAID:
            return True
        return False

    def manage_amounts(self):
        """
        Set total and amount of the :class:`~invoicing.models.Invoice`.

        Includes :class:`~invoicing.models.InvoiceItem`\ 's unit prices and taxes.

        Invoice checks for related down-payments and substracts their individual amounts to its amount.
        """
        super(Invoice, self).manage_amounts()
        # Substract down-payment invoice amounts from amount
        if self.related_quotation:
            for down_payment in self.related_quotation.down_payments:
                self.amount -= down_payment.amount
        self.balance = self.amount - self.paid

    def manage_paid(self):
        self.paid = Decimal("0.00")
        for payment in self.payments:
            self.paid += payment.amount

        # Updates balance in case of payment changes
        self.balance = self.amount - self.paid

        # Manage state changes
        if self.state != Invoice.STATES.CANCELLED:
            if self.paid > 0 and self.balance > 0 and self.state not in (Invoice.STATES.PART_PAID, Invoice.STATES.OVERDUE):
                self.state = Invoice.STATES.PART_PAID
            elif self.paid > 0 and self.balance == 0 and self.state != Invoice.STATES.PAID:
                self.state = Invoice.STATES.PAID

    def get_possible_states(self):
        """
        List the available states for the :class:`~invoicing.models.Invoice`,
        depending of its current state.
        """
        if self.state == Invoice.STATES.DRAFT:
            return [Invoice.STATES.REGISTERED]
        elif self.state == Invoice.STATES.REGISTERED:
            return [Invoice.STATES.CANCELLED]
        elif self.state == Invoice.STATES.OVERDUE:
            return [Invoice.STATES.CANCELLED]
        elif self.state == Invoice.STATES.PART_PAID:
            return [Invoice.STATES.CANCELLED]
        elif self.state == Invoice.STATES.PAID:
            return [Invoice.STATES.CANCELLED]
        else:
            return []

    def cancel(self, issuer):
        """
        Cancel the :class:`~invoicing.models.Invoice` with the creation of an
        associated :class:`~invoicing.models.CreditNote`
        """
        from invoicing.models.credit_note import CreditNote
        if not self.is_cancelable():
            raise NotCancelableInvoice("Invoice is not cancelable.")
        credit_note = CreditNote(
            full_init=False,
            tenant=self.tenant,
            account_type=self.account_type,
            issuer=issuer,
            organization=self.organization,
            contact=self.contact,
            related_invoice=self
        )
        cn_data = credit_note.add_revision(revision=self.current_revision)
        cn_data.issuer = issuer
        cn_data.issue_date = datetime_now()
        cn_data.credit_note_emission_date = datetime.date.today()
        for item in cn_data.line_items:
            if not isinstance(item.reference, basestring):
                item.reference = unicode(item.reference)
            item.unit_price = -item.unit_price
        credit_note.save()
        self.update(set__related_credit_note=credit_note)
        self.set_state(Invoice.STATES.CANCELLED, True)
        invoicing_signals.post_cancel_invoice.send(self.__class__, document=self, credit_note=credit_note)
        return credit_note

    @classmethod
    def post_register_invoice(cls, sender, document, previous_state, **kwargs):
        post_register_invoice_task.delay(document, previous_state)

    @classmethod
    def post_cancel_invoice(cls, sender, document, credit_note, **kwargs):
        """
        Post cancel invoice hook handler

        - Update related quotation state, if invoice
        - Add timeline and notification entries
        """
        # Update related quotation state, if invoice
        if document.is_invoice() and document.related_quotation:
            # Removes invoiced state
            document.related_quotation.remove_invoiced_state()
            # Manage cancelled related invoice
            document.related_quotation.related_invoices_cancelled.append(document)
            document.related_quotation.related_invoice = None
            # Saves updates
            document.related_quotation.save()

        # Add timeline and notification entries
        post_cancel_invoice_task.delay(document, credit_note)

    @staticmethod
    def manage_states():
        """
        An :class:`~invoicing.models.Invoice` state can be modified by the time.

        This method allows tasks scripts to update Invoices state on a regular basis.
        """
        today = datetime.date.today()
        Invoice.objects\
            .filter(state__in=[Invoice.STATES.REGISTERED, Invoice.STATES.PART_PAID], current_revision__due_date__lt=today)\
            .update(set__state=Invoice.STATES.OVERDUE)

    @staticmethod
    def full_export(tenant, start_date=None, end_date=None):
        def get_path(invoice):
            invoicing_date = invoice.current_revision.invoicing_date or invoice.current_revision.issue_date
            return '{0}/{1}/{2}'.format(ugettext('Invoices'), invoicing_date.strftime('%Y/%m'), invoice.filename)

        def get_doc(invoice):
            return invoice.gen_pdf().getvalue()

        kwargs = {'tenant': tenant}
        if start_date:
            kwargs.update(current_revision__invoicing_date__gte=start_date)
        if end_date:
            kwargs.update(current_revision__invoicing_date__lt=end_date)
        queryset = Invoice.objects.filter(**kwargs)
        return queryset, get_path, get_doc
