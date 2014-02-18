# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.timezone import now as datetime_now
from mongoengine import fields
import datetime

from vosae_utils import SearchDocumentMixin
from pyes import mappings as search_mappings

from invoicing.exceptions import InvalidInvoiceBaseState
from invoicing.models.invoice_base import InvoiceBase
from invoicing.models.mixins import InvoiceMakableMixin
from invoicing.tasks import post_make_purchase_order_task
from invoicing import QUOTATION_STATES


__all__ = ('Quotation',)


class Quotation(InvoiceBase, InvoiceMakableMixin, SearchDocumentMixin):

    """Quotations specific class."""
    TYPE = "QUOTATION"
    RECORD_NAME = _("Quotation")
    STATES = QUOTATION_STATES
    DEFAULT_STATE = QUOTATION_STATES.DRAFT
    QUOTATION_VALIDITY_PERIODS = (15, 30, 45, 60, 90)

    state = fields.StringField(required=True, choices=STATES, default=DEFAULT_STATE)
    current_revision = fields.EmbeddedDocumentField("QuotationRevision", required=True)
    revisions = fields.ListField(fields.EmbeddedDocumentField("QuotationRevision"))

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
        if self.group.invoice:
            kwargs.update(related_invoice_reference=self.group.invoice.reference)
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

        If created:

        - increments the appropriate :class:`~core.models.Tenant` quotations numbering counter.
        - set the quotation to the group
        """
        if created:
            document.tenant.tenant_settings.increment_quotation_counter()
            document.group.quotation = document
            document.group.save()

        # Calling parent
        super(Quotation, document).post_save(sender, document, created, **kwargs)

    @classmethod
    def post_delete(self, sender, document, **kwargs):
        """
        Post delete hook handler

        - Update group relations
        """
        # Update group relations
        document.group.deleted_documents.append(document)
        document.group.quotation = None
        document.group.save()

        # Calling parent
        super(Quotation, document).post_delete(sender, document, **kwargs)

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
        if self.group.invoice:
            return False
        return True

    def is_deletable(self):
        """
        A :class:`~invoicing.models.Quotation` is deletable if not linked to any
        :class:`~invoicing.models.Invoice` or :class:`~invoicing.models.DownPaymentInvoice`.
        """
        if self.group.invoice or self.group.down_payment_invoices:
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

    def make_purchase_order(self, issuer):
        """Creates a purchase order based on the current quotation"""
        from invoicing.models import PurchaseOrder, PurchaseOrderRevision

        # Initialize the purchase order
        purchase_order = PurchaseOrder(
            full_init=False,
            tenant=self.tenant,
            account_type=self.account_type,
            issuer=issuer,
            organization=self.organization,
            contact=self.contact,
            group=self.group,
            attachments=self.attachments
        )
        
        # Save the purchase order, based on the quotation
        purchase_order_data = purchase_order.add_revision(revision=PurchaseOrderRevision(based_on=self.current_revision))
        purchase_order_data.state = purchase_order.state
        purchase_order_data.issuer = issuer
        purchase_order_data.issue_date = datetime_now()
        purchase_order_data.purchase_order_date = datetime.date.today()
        purchase_order.save()
        return purchase_order

    @classmethod
    def post_make_purchase_order(cls, sender, issuer, document, new_document, **kwargs):
        """
        Post make purchase order hook handler

        - Add timeline and notification entries
        """
        # Add timeline and notification entries
        post_make_purchase_order_task.delay(issuer, document, new_document)

    @staticmethod
    def manage_states():
        """
        An :class:`~invoicing.models.Quotation` state can be modified by the time.

        This method allows tasks scripts to update Quotations state on a regular basis.
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
