# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.timezone import now as datetime_now
from mongoengine import fields
from decimal import Decimal, ROUND_HALF_UP
import datetime

from vosae_utils import SearchDocumentMixin
from pyes import mappings as search_mappings

from invoicing.exceptions import *
from invoicing.models.invoice_base import InvoiceBase
from invoicing import signals as invoicing_signals
from invoicing import QUOTATION_STATES, get_due_date
from invoicing.tasks import post_make_invoice_task


__all__ = ('Quotation',)


class Quotation(InvoiceBase, SearchDocumentMixin):

    """Quotations specific class."""
    TYPE = "QUOTATION"
    RECORD_NAME = _("Quotation")
    STATES = QUOTATION_STATES
    QUOTATION_VALIDITY_PERIODS = (15, 30, 45, 60, 90)

    state = fields.StringField(required=True, choices=STATES, default=STATES.DRAFT)
    related_invoice = fields.ReferenceField("Invoice")
    related_invoices_cancelled = fields.ListField(fields.ReferenceField("Invoice"))
    down_payments = fields.ListField(fields.ReferenceField("DownPaymentInvoice"))

    meta = {
        "allow_inheritance": True
    }

    class Meta():
        document_type = 'quotation'
        document_boost = 0.9
        fields = [
            search_mappings.StringField(name="reference", boost=document_boost * 3.0, index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="related_invoice_reference", boost=document_boost * 1.5, index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="contact", index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="organization", index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.DateField(name="quotation_date", index="analyzed", term_vector="with_positions_offsets", include_in_all=False),
            search_mappings.StringField(name="state", index="not_analyzed", term_vector="with_positions_offsets", include_in_all=False),
        ]

    class InvalidState(InvalidInvoiceBaseState):

        def __init__(self, **kwargs):
            super(Quotation.InvalidState, self).__init__(**kwargs)
            self.message = 'Invalid quotation state'

    def get_search_kwargs(self):
        kwargs = super(Quotation, self).get_search_kwargs()
        if self.current_revision.quotation_date:
            kwargs.update(quotation_date=self.current_revision.quotation_date)
        if self.related_invoice:
            kwargs.update(related_invoice_reference=self.related_invoice.reference)
        return kwargs

    @classmethod
    def pre_save(self, sender, document, **kwargs):
        """
        Pre save hook handler

        - Set the type and reference
        """
        # Calling parent
        super(Quotation, document).pre_save(sender, document, **kwargs)

        if not document.is_created():
            document.base_type = document.TYPE
            document.reference = document.genere_reference(document.tenant.tenant_settings)

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        """
        Post save hook handler

        If created, increments the appropriate :class:`~core.models.Tenant`
        quotations numbering counter.
        """
        if created:
            document.tenant.tenant_settings.increment_quotation_counter()

        # Calling parent
        super(Quotation, document).post_save(sender, document, created, **kwargs)

    def genere_reference(self, tenant_settings):
        """
        Genere a unique reference for an :class:`~invoicing.models.Quotation` object.

        Use the :class:`~core.models.Tenant` quotations numbering counter.
        """
        if tenant_settings.invoicing.numbering.scheme == "DN":
            date = unicode(datetime.datetime.strftime(datetime.datetime.now(), tenant_settings.invoicing.numbering.DATE_STRFTIME_FORMATS[tenant_settings.invoicing.numbering.date_format]))
            counter = unicode("%0*d" % (5, tenant_settings.get_quotation_counter()))
            elements = (date, counter)
        elif tenant_settings.invoicing.numbering.scheme == "N":
            counter = unicode("%0*d" % (5, tenant_settings.get_quotation_counter()))
            elements = (counter,)
        else:
            return False
        return unicode(tenant_settings.invoicing.numbering.separator).join(elements)

    def is_quotation(self):
        return True

    def is_modifiable(self):
        """A :class:`~invoicing.models.Quotation` is modifiable unless it has been invoiced."""
        if self.related_invoice:
            return False
        return True

    def is_deletable(self):
        """
        A :class:`~invoicing.models.Quotation` is deletable if not linked to any
        :class:`~invoicing.models.Invoice` or :class:`~invoicing.models.DownPaymentInvoice`.
        """
        if self.related_invoice or self.down_payments:
            return False
        return True

    def is_issuable(self):
        """Determine if the :class:`~invoicing.models.Quotation` could be sent."""
        if self.state not in (Quotation.STATES.DRAFT,):
            return True
        return False

    def get_possible_states(self):
        """
        List the available states for the :class:`~invoicing.models.Quotation`,
        depending of its current state.
        """
        if self.state == Quotation.STATES.DRAFT:
            return [Quotation.STATES.AWAITING_APPROVAL, Quotation.STATES.APPROVED, Quotation.STATES.REFUSED]
        elif self.state == Quotation.STATES.AWAITING_APPROVAL:
            return [Quotation.STATES.APPROVED, Quotation.STATES.REFUSED]
        elif self.state == Quotation.STATES.EXPIRED:
            return [Quotation.STATES.AWAITING_APPROVAL, Quotation.STATES.APPROVED, Quotation.STATES.REFUSED]
        elif self.state == Quotation.STATES.REFUSED:
            return [Quotation.STATES.AWAITING_APPROVAL, Quotation.STATES.APPROVED]
        else:
            return []

    def make_invoice(self, issuer):
        """Creates an invoice based on the current quotation"""
        from invoicing.models.invoice import Invoice
        # Initialize the invoice
        invoice = Invoice(
            full_init=False,
            tenant=self.tenant,
            account_type=self.account_type,
            issuer=issuer,
            organization=self.organization,
            contact=self.contact,
            related_quotation=self,
            attachments=self.attachments
        )
        # Save the invoice, based on the quotation
        inv_data = invoice.add_revision(revision=self.current_revision)
        inv_data.state = invoice.state
        inv_data.issuer = issuer
        inv_data.issue_date = datetime_now()
        inv_data.invoicing_date = datetime.date.today()
        inv_data.due_date = get_due_date(inv_data.invoicing_date, self.tenant.tenant_settings.invoicing.payment_conditions)
        invoice.save()
        # Update quotation with related invoice
        self.state = Quotation.STATES.INVOICED
        self.related_invoice = invoice
        self.save()
        return invoice

    def make_down_payment(self, issuer, percentage, tax, date):
        """Creates a down payment invoice based on the current quotation"""
        from invoicing.models.down_payment_invoice import DownPaymentInvoice
        if percentage <= 0 or percentage >= 1:
            raise InvalidDownPaymentPercentage("Percentage must be a decimal between 0 and 1.")
        inv_data = self.current_revision
        # Calculate the total amount from the base (excluding taxes) to avoid decimal differences.
        # Check with amount=97.72 and tax_rate=0.196.
        excl_tax_amount = ((self.amount * percentage).quantize(Decimal('1.00'), ROUND_HALF_UP) / (Decimal('1.00') + tax.rate)).quantize(Decimal('1.00'), ROUND_HALF_UP)
        down_payment_amount = (excl_tax_amount * (Decimal('1.00') + tax.rate)).quantize(Decimal('1.00'), ROUND_HALF_UP)
        current_percentage = Decimal('0.00')
        for down_payment in self.down_payments:
            current_percentage += down_payment.percentage
        if current_percentage + percentage > 1:
            raise InvalidDownPaymentPercentage("Total of down-payments percentages exceeds 1 (100%).")
        if date < datetime.date.today() or (date > inv_data.due_date if inv_data.due_date else False):
            raise InvalidDownPaymentDueDate("Invalid down-payment due date.")
        down_payment = DownPaymentInvoice(
            full_init=False,
            tenant=self.tenant,
            account_type=self.account_type,
            issuer=issuer,
            state="REGISTERED",
            organization=self.organization,
            contact=self.contact,
            related_quotation=self,
            percentage=percentage,
            tax_applied=tax,
            total=down_payment_amount,
            amount=down_payment_amount,
            balance=down_payment_amount
        )

        down_payment.add_revision(
            state=down_payment.state,
            issuer=issuer,
            issue_date=datetime_now(),
            sender=inv_data.sender,
            organization=inv_data.organization,
            contact=inv_data.contact,
            sender_address=inv_data.sender_address,
            billing_address=inv_data.billing_address,
            delivery_address=inv_data.delivery_address,
            customer_reference=inv_data.customer_reference,
            currency=inv_data.currency,
            invoicing_date=inv_data.invoicing_date or date.today(),
            due_date=date
        )
        # Save the down payment invoice
        down_payment.save()
        # Update quotation with related down-payment invoice
        self.down_payments.append(down_payment)
        self.save()
        invoicing_signals.post_make_down_payment_invoice.send(self.__class__, document=self, new_document=down_payment)
        return down_payment

    @classmethod
    def post_make_invoice(cls, sender, document, new_document, **kwargs):
        """
        Post make invoice hook handler

        - Add timeline and notification entries
        """
        # Add timeline and notification entries
        post_make_invoice_task.delay(document, new_document)

    @classmethod
    def post_make_down_payment_invoice(cls, sender, document, new_document, **kwargs):
        """
        Post make down payment invoice hook handler

        - Add timeline and notification entries
        - Add a statistic entry
        """
        from vosae_statistics.models import DownPaymentInvoiceStatistics

        # Add timeline and notification entries
        post_make_invoice_task.delay(document, new_document)

        # Saves statistic
        DownPaymentInvoiceStatistics(
            tenant=new_document.tenant,
            date=new_document.current_revision.invoicing_date,
            amount=new_document.amount,
            organization=new_document.organization,
            contact=new_document.contact,
            location=new_document.current_revision.billing_address if new_document.account_type == 'RECEIVABLE' else new_document.current_revision.sender_address,
            account_type=new_document.account_type,
            down_payment_invoice=new_document
        ).save()

    @staticmethod
    def manage_states():
        """
        An :class:`~invoicing.models.Invoice` state can be modified by the time.

        This method allows tasks scripts to update Invoices state on a regular basis.
        """
        today = datetime.date.today()
        Quotation.objects\
            .filter(state=Quotation.STATES.AWAITING_APPROVAL, current_revision__quotation_validity__lt=today)\
            .update(set__state=Quotation.STATES.EXPIRED)

    @staticmethod
    def full_export(tenant, start_date=None, end_date=None):
        def get_path(quotation):
            quotation_date = quotation.current_revision.quotation_date or quotation.current_revision.issue_date
            return '{0}/{1}/{2}'.format(ugettext('Quotations'), quotation_date.strftime('%Y/%m'), quotation.filename)

        def get_doc(quotation):
            return quotation.gen_pdf().getvalue()

        kwargs = {'tenant': tenant}
        if start_date:
            kwargs.update(current_revision__quotation_date__gte=start_date)
        if end_date:
            kwargs.update(current_revision__quotation_date__lt=end_date)
        queryset = Quotation.objects.filter(**kwargs)
        return queryset, get_path, get_doc

    def remove_invoiced_state(self):
        if self.current_revision.quotation_validity and self.current_revision.quotation_validity < datetime.date.today():
            self.state = QUOTATION_STATES.EXPIRED
        else:
            self.state = QUOTATION_STATES.APPROVED
