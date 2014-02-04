# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext_lazy as _, ugettext
from mongoengine import fields
import datetime

from vosae_utils import SearchDocumentMixin
from pyes import mappings as search_mappings

from invoicing.exceptions import *
from invoicing.models.invoice_base import InvoiceBase
from invoicing.models.mixins import InvoiceMakableMixin
from invoicing import PURCHASE_ORDER_STATES


__all__ = ('PurchaseOrder',)


class PurchaseOrder(InvoiceBase, InvoiceMakableMixin, SearchDocumentMixin):

    """Purchase orders specific class."""
    TYPE = "PURCHASE_ORDER"
    RECORD_NAME = _("Purchase order")
    STATES = PURCHASE_ORDER_STATES

    state = fields.StringField(required=True, choices=STATES, default=STATES.DRAFT)
    current_revision = fields.EmbeddedDocumentField("PurchaseOrderRevision", required=True)
    revisions = fields.ListField(fields.EmbeddedDocumentField("PurchaseOrderRevision"))

    meta = {
        "allow_inheritance": True
    }

    class Meta():
        document_type = 'purchase_order'
        document_boost = 0.9
        fields = [
            search_mappings.StringField(name="reference", boost=document_boost * 3.0, index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="related_quotation_reference", boost=document_boost * 1.5, index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="related_invoice_reference", boost=document_boost * 1.5, index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="contact", index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.StringField(name="organization", index="analyzed", term_vector="with_positions_offsets"),
            search_mappings.DateField(name="purchase_order_date", index="analyzed", term_vector="with_positions_offsets", include_in_all=False),
            search_mappings.StringField(name="state", index="not_analyzed", term_vector="with_positions_offsets", include_in_all=False),
        ]

    class InvalidState(InvalidInvoiceBaseState):

        def __init__(self, **kwargs):
            super(PurchaseOrder.InvalidState, self).__init__(**kwargs)
            self.message = 'Invalid purchase order state'

    def get_search_kwargs(self):
        kwargs = super(PurchaseOrder, self).get_search_kwargs()
        if self.current_revision.purchase_order_date:
            kwargs.update(purchase_order_date=self.current_revision.purchase_order_date)
        if self.group.quotation:
            kwargs.update(related_quotation_reference=self.group.quotation.reference)
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
        super(PurchaseOrder, document).pre_save(sender, document, **kwargs)

        if not document.is_created():
            document.base_type = document.TYPE
            document.reference = document.genere_reference(document.tenant.tenant_settings)

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        """
        Post save hook handler

        If created:

        - increments the appropriate :class:`~core.models.Tenant` purchase orders numbering counter.
        - set the purchase order to the group
        """
        if created:
            document.tenant.tenant_settings.increment_purchase_order_counter()
            document.group.purchase_order = document
            document.group.save()

        # Calling parent
        super(PurchaseOrder, document).post_save(sender, document, created, **kwargs)

    def genere_reference(self, tenant_settings):
        """
        Genere a unique reference for an :class:`~invoicing.models.PurchaseOrder` object.

        Use the :class:`~core.models.Tenant` purchase order numbering counter.
        """
        if tenant_settings.invoicing.numbering.scheme == "DN":
            date = unicode(datetime.datetime.strftime(datetime.datetime.now(), tenant_settings.invoicing.numbering.DATE_STRFTIME_FORMATS[tenant_settings.invoicing.numbering.date_format]))
            counter = unicode("%0*d" % (5, tenant_settings.get_purchase_order_counter()))
            elements = (date, counter)
        elif tenant_settings.invoicing.numbering.scheme == "N":
            counter = unicode("%0*d" % (5, tenant_settings.get_purchase_order_counter()))
            elements = (counter,)
        else:
            return False
        return unicode(tenant_settings.invoicing.numbering.separator).join(elements)

    def is_purchase_order(self):
        """True if the :class:`~invoicing.models.PurchaseOrder` is a quotation object (and not an inherited)."""
        if isinstance(self, PurchaseOrder):
            return True
        return False

    def is_purchase_order_instance(self):
        """True if the :class:`~invoicing.models.PurchaseOrder` is an instance of :class:`~invoicing.models.PurchaseOrder`."""
        return True

    def is_modifiable(self):
        """A :class:`~invoicing.models.PurchaseOrder` is modifiable unless it has been invoiced."""
        if self.group.invoice:
            return False
        return True

    def is_deletable(self):
        """
        A :class:`~invoicing.models.PurchaseOrder` is deletable if not linked to any
        :class:`~invoicing.models.Invoice` or :class:`~invoicing.models.DownPaymentInvoice`.
        """
        if self.group.invoice or self.group.down_payment_invoices:
            return False
        return True

    def is_issuable(self):
        """Determine if the :class:`~invoicing.models.PurchaseOrder` could be sent."""
        if self.state not in (PurchaseOrder.STATES.DRAFT,):
            return True
        return False

    def get_possible_states(self):
        """
        List the available states for the :class:`~invoicing.models.PurchaseOrder`,
        depending of its current state.
        """
        if self.state == PurchaseOrder.STATES.DRAFT:
            return [PurchaseOrder.STATES.AWAITING_APPROVAL, PurchaseOrder.STATES.APPROVED, PurchaseOrder.STATES.REFUSED]
        elif self.state == PurchaseOrder.STATES.AWAITING_APPROVAL:
            return [PurchaseOrder.STATES.APPROVED, PurchaseOrder.STATES.REFUSED]
        elif self.state == PurchaseOrder.STATES.REFUSED:
            return [PurchaseOrder.STATES.AWAITING_APPROVAL, PurchaseOrder.STATES.APPROVED]
        else:
            return []

    @staticmethod
    def full_export(tenant, start_date=None, end_date=None):
        def get_path(purchase_order):
            purchase_order_date = purchase_order.current_revision.purchase_order_date or purchase_order.current_revision.issue_date
            return '{0}/{1}/{2}'.format(ugettext('Purchase orders'), purchase_order_date.strftime('%Y/%m'), purchase_order.filename)

        def get_doc(purchase_order):
            return purchase_order.gen_pdf().getvalue()

        kwargs = {'tenant': tenant}
        if start_date:
            kwargs.update(current_revision__purchase_order_date__gte=start_date)
        if end_date:
            kwargs.update(current_revision__purchase_order_date__lt=end_date)
        queryset = PurchaseOrder.objects.filter(**kwargs)
        return queryset, get_path, get_doc

    def remove_invoiced_state(self):
        self.state = PURCHASE_ORDER_STATES.APPROVED
