# -*- coding:Utf-8 -*-

from django.utils.timezone import now as datetime_now
from decimal import Decimal, ROUND_HALF_UP
import datetime

from invoicing.exceptions import InvalidDownPaymentPercentage, InvalidDownPaymentDueDate
from invoicing import signals as invoicing_signals
from invoicing import QUOTATION_STATES, PURCHASE_ORDER_STATES, get_due_date
from invoicing.tasks import post_make_invoice_task


__all__ = ('InvoiceMakableMixin',)


class InvoiceMakableMixin(object):

    """Mixin used for both quotations and purchase orders to generate invoices from their current revision"""

    def make_invoice(self, issuer):
        """Creates an invoice based on the current quotation/purchase order"""
        from invoicing.models.invoice import Invoice
        # Initialize the invoice
        invoice = Invoice(
            full_init=False,
            tenant=self.tenant,
            account_type=self.account_type,
            issuer=issuer,
            organization=self.organization,
            contact=self.contact,
            related_to=self,
            group=self.group,
            attachments=self.attachments
        )
        
        # Save the invoice, based on the quotation/purchase order
        inv_data = invoice.add_revision(revision=self.current_revision)
        inv_data.state = invoice.state
        inv_data.issuer = issuer
        inv_data.issue_date = datetime_now()
        inv_data.invoicing_date = datetime.date.today()
        inv_data.due_date = get_due_date(inv_data.invoicing_date, self.tenant.tenant_settings.invoicing.payment_conditions)
        invoice.save()
        
        # Update state
        if self.is_quotation():
            self.state = QUOTATION_STATES.INVOICED
        elif self.is_purchase_order():
            self.state = PURCHASE_ORDER_STATES.INVOICED
        self.save()
        return invoice

    def make_down_payment_invoice(self, issuer, percentage, tax, date):
        """Creates a down payment invoice based on the current quotation/purchase order"""
        from invoicing.models.down_payment_invoice import DownPaymentInvoice
        if percentage <= 0 or percentage >= 1:
            raise InvalidDownPaymentPercentage("Percentage must be a decimal between 0 and 1.")
        inv_data = self.current_revision
        
        # Calculate the total amount from the base (excluding taxes) to avoid decimal differences.
        # Check with amount=97.72 and tax_rate=0.196.
        excl_tax_amount = ((self.amount * percentage).quantize(Decimal('1.00'), ROUND_HALF_UP) / (Decimal('1.00') + tax.rate)).quantize(Decimal('1.00'), ROUND_HALF_UP)
        down_payment_amount = (excl_tax_amount * (Decimal('1.00') + tax.rate)).quantize(Decimal('1.00'), ROUND_HALF_UP)
        
        # Sum existing down payments percentage
        current_percentage = Decimal('0.00')
        for down_payment_invoice in self.group.down_payment_invoices:
            current_percentage += down_payment_invoice.percentage
        
        # Ensure that down payments can't exceed 100%
        if current_percentage + percentage > 1:
            raise InvalidDownPaymentPercentage("Total of down-payments percentages exceeds 1 (100%).")
        
        # Ensure that date is correct
        if date < datetime.date.today() or (date > inv_data.due_date if inv_data.due_date else False):
            raise InvalidDownPaymentDueDate("Invalid down-payment due date.")
        down_payment_invoice = DownPaymentInvoice(
            full_init=False,
            tenant=self.tenant,
            account_type=self.account_type,
            issuer=issuer,
            state="REGISTERED",
            organization=self.organization,
            contact=self.contact,
            related_to=self,
            percentage=percentage,
            tax_applied=tax,
            total=down_payment_amount,
            amount=down_payment_amount,
            balance=down_payment_amount,
            group=self.group,
            attachments=self.attachments
        )

        down_payment_invoice.add_revision(
            state=down_payment_invoice.state,
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
        down_payment_invoice.save()
        return down_payment_invoice

    @classmethod
    def post_make_invoice(cls, sender, issuer, document, new_document, **kwargs):
        """
        Post make invoice hook handler

        - Add timeline and notification entries
        """
        # Add timeline and notification entries
        post_make_invoice_task.delay(issuer, document, new_document)

    @classmethod
    def post_make_down_payment_invoice(cls, sender, issuer, document, new_document, **kwargs):
        """
        Post make down payment invoice hook handler

        - Add timeline and notification entries
        - Add a statistic entry
        """
        from vosae_statistics.models import DownPaymentInvoiceStatistics

        # Add timeline and notification entries
        post_make_invoice_task.delay(issuer, document, new_document)

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
