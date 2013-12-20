# -*- coding:Utf-8 -*-

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.utils.translation import pgettext_lazy
from django.utils.timezone import now as datetime_now
from django.core.files.base import ContentFile
from django.template import Template, Context
from django.core.mail import EmailMessage
from mongoengine import Document, fields, PULL
from decimal import Decimal, ROUND_HALF_UP
import uuid

from core.mixins import AsyncTTLUploadsMixin
from core.tasks import es_document_index, es_document_deindex
from core.fields import NotPrivateReferenceField

from invoicing import ACCOUNT_TYPES, HISTORY_STATES, STATES_RESET_CACHED_DATA, INVOICE_STATES
from invoicing import signals as invoicing_signals
from invoicing.models.embedded.invoice_history_entries import *
from invoicing.exceptions import NotDeletableInvoice
from invoicing.tasks import (
    invoicebase_changed_state_task,
    invoicebase_deleted_task
)

from notification.mixins import NotificationAwareDocumentMixin
from vosae_utils import respect_language


__all__ = ('InvoiceBase', 'InvoiceBaseGroup')



class InvoiceBaseGroup(Document):

    """Group of all :class:`~invoicing.models.InvoiceBase` related documents."""

    tenant = fields.ReferenceField("Tenant", required=True)
    quotation = fields.ReferenceField("Quotation")
    purchase_order = fields.ReferenceField("PurchaseOrder")
    down_payment_invoices = fields.ListField(fields.ReferenceField("DownPaymentInvoice"))
    invoice = fields.ReferenceField("Invoice")
    invoices_cancelled = fields.ListField(fields.ReferenceField("Invoice"))
    credit_notes = fields.ListField(fields.ReferenceField("CreditNote"))


class InvoiceBase(Document, AsyncTTLUploadsMixin, NotificationAwareDocumentMixin):

    """Base class for all quotations and invoices (either payable or receivable)."""
    ACCOUNT_TYPES = ACCOUNT_TYPES
    SENDING_VARS = (
        ("{{ reference }}", pgettext_lazy("invoicing sending vars", "{Reference}")),
        ("{{ signature|default:'' }}", pgettext_lazy("invoicing sending vars", "{Signature}")),
        ("{{ invoicing_date|date:'DATE_FORMAT'|default:'' }}", pgettext_lazy("invoicing sending vars", "{Invoicing_Date}"))
    )
    RELATED_WITH_TTL = ['attachments']

    tenant = fields.ReferenceField("Tenant", required=True)
    base_type = fields.StringField(required=True, choices=("QUOTATION", "PURCHASE_ORDER", "INVOICE", "CREDIT_NOTE"))
    reference = fields.StringField(required=True, unique_with=["tenant", "base_type"])
    account_type = fields.StringField(required=True, choices=ACCOUNT_TYPES)
    total = fields.DecimalField(required=True)
    amount = fields.DecimalField(required=True)
    issuer = fields.ReferenceField("VosaeUser")
    organization = NotPrivateReferenceField("Organization")
    contact = NotPrivateReferenceField("Contact")
    history = fields.ListField(fields.EmbeddedDocumentField("InvoiceHistoryEntry"))
    notes = fields.ListField(fields.EmbeddedDocumentField("InvoiceNote"))
    group = fields.ReferenceField("InvoiceBaseGroup", required=True, default=lambda: InvoiceBaseGroup())
    attachments = fields.ListField(fields.ReferenceField("VosaeFile", reverse_delete_rule=PULL))

    meta = {
        "indexes": ["tenant", "account_type", "amount", "issuer", "organization", "contact"],
        "allow_inheritance": True,

        # Vosae specific
        "vosae_permissions": ("see_invoicebase", "add_invoicebase", "change_invoicebase", "delete_invoicebase", "transmit_invoicebase", "post_invoicebase"),
        "vosae_mandatory_permissions": ("invoicing_access",),
        "vosae_timeline_permission": "see_invoicebase",
    }

    def __unicode__(self):
        return self.reference

    def __init__(self, full_init=True, *args, **kwargs):
        super(InvoiceBase, self).__init__(*args, **kwargs)
        if not self.is_created() and full_init:
            self.add_revision(issuer=self.issuer, issue_date=datetime_now())

    def delete(self, *args, **kwargs):
        """Some :class:`~invoicing.models.InvoiceBase` can only be deleted according to some rules."""
        if not self.is_deletable():
            raise NotDeletableInvoice("This record is not in a deletable state")
        super(InvoiceBase, self).delete(*args, **kwargs)

    @classmethod
    def pre_save(self, sender, document, **kwargs):
        """
        Pre save hook handler  
        On creation:

        - Add issuer to subscribers list
        - Add organization name to revision
        - Manage total / amount
        """
        if not document.is_created() or document.is_modifiable():
            # Add issuer to subscribers list
            if not document.current_revision.issuer in document.subscribers:
                document.subscribers.append(document.current_revision.issuer)

            # Add organization name to revision
            if document.account_type == 'PAYABLE':
                if document.organization:
                    document.current_revision.sender_organization = document.organization.corporate_name
            else:
                document.current_revision.sender_organization = document.tenant.name

            # Manage total / amount
            document.manage_amounts()
        
        # If newly created saves the related group before
        if not document.group.id or not document.group.tenant:
            document.group.tenant = document.tenant
            document.group.save()

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        """
        Post save hook handler

        - Removes related TTL
        - Index invoice based document in elasticsearch
        - Add timeline and notification entries
        """
        # Removes related TTL
        document.remove_related_ttl()

        # Index invoice based document in elasticsearch
        es_document_index.delay(document)

    @classmethod
    def post_delete(self, sender, document, **kwargs):
        """
        Post delete hook handler

        - Deletes related attachments, if exists
        - De-index invoice based document from elasticsearch
        - Removes timeline and notification entries
        """
        # Deletes related attachments, if exists
        for attachment in document.attachments:
            attachment.delete()

        # De-index invoice based document from elasticsearch
        es_document_deindex.delay(document)

        # Removes timeline and notification entries
        invoicebase_deleted_task.delay(document)

    @classmethod
    def post_client_changed_invoice_state(cls, sender, issuer, document, previous_state, **kwargs):
        """
        Post client changed invoice state hook handler

        - Fire invoice registration signal
        - Add timeline and notification entries
        """
        # Fire invoice registration signal
        if document.is_invoice() and previous_state == INVOICE_STATES.DRAFT and document.state == INVOICE_STATES.REGISTERED:
            invoicing_signals.post_register_invoice.send(sender, issuer=issuer, document=document, previous_state=previous_state)

        # Add timeline and notification entries
        invoicebase_changed_state_task.delay(issuer, document, previous_state)

    def get_search_kwargs(self):
        kwargs = {
            'reference': self.reference,
            'state': self.state
        }
        if self.contact:
            kwargs.update(contact=self.contact.get_full_name())
        if self.organization:
            kwargs.update(organization=self.organization.corporate_name)
        return kwargs

    def add_changed_state_history_entry(self):
        if self.state in HISTORY_STATES:
            self.history.insert(0, ChangedStateHistoryEntry(
                state=self.state,
                issuer=self.current_revision.issuer,
                revision=self.current_revision.revision
            ))

    def add_sent_history_entry(self, method, to):
        self.history.insert(0, SentHistoryEntry(
            sent_method=method,
            sent_to=to,
            issuer=self.current_revision.issuer,
            revision=self.current_revision.revision
        ))

    def reload(self, *args, **kwargs):
        """
        Reload the :class:`~invoicing.models.Invoice` from the database.

        Delete the existing cached attributes.
        """
        super(InvoiceBase, self).reload()
        if hasattr(self, "_sub_total"):
            del self._sub_total
        if hasattr(self, "_taxes_amounts"):
            del self._taxes_amounts

    def is_created(self):
        """
        True if the :class:`~invoicing.models.Invoice` is already saved
        (e.g. exists in the database).
        """
        if self.id:
            return True
        return False

    def is_modifiable(self):
        """
        Determine if the :class:`~invoicing.models.InvoiceBase` could be modified.  
        Always True in the base class.
        """
        return True

    def is_deletable(self):
        """
        Determine if the :class:`~invoicing.models.InvoiceBase` could be deleted.  
        Always False in the base class.
        """
        return False

    def is_cancelable(self):
        """
        Determine if the :class:`~invoicing.models.InvoiceBase` could be canceled.  
        Always False in the base class.
        """
        return False

    def is_issuable(self):
        """
        Determine if the :class:`~invoicing.models.InvoiceBase` could be sent.  
        Always False in the base class.
        """
        return False

    def is_quotation(self):
        """Always False in the base class."""
        return False

    def is_purchase_order(self):
        """Always False in the base class."""
        return False

    def is_invoice(self):
        """Always False in the base class."""
        return False

    def is_down_payment_invoice(self):
        """Always False in the base class."""
        return False

    def is_credit_note(self):
        """Always False in the base class."""
        return False

    @property
    def sub_total(self):
        """
        Do a sum of the :class:`~invoicing.models.InvoiceItem` prices and cache it.

        This does not contains taxes.
        """
        if not hasattr(self, "_sub_total"):
            self._sub_total = 0
            current_revision = self.current_revision
            if current_revision:
                for line_item in current_revision.line_items:
                    if line_item.optional:
                        continue
                    self._sub_total += (line_item.quantity * line_item.unit_price).quantize(Decimal('1.00'), ROUND_HALF_UP)
        return self._sub_total

    @property
    def taxes_amounts(self):
        """
        Do a sum of the :class:`~invoicing.models.InvoiceItem` taxes and cache it.

        This does not contains :class:`~invoicing.models.InvoiceItem` unit prices.
        """
        if not hasattr(self, "_taxes_amounts"):
            taxes_amounts = {}
            current_revision = self.current_revision
            if current_revision:
                for item in current_revision.line_items:
                    if taxes_amounts.get(str(item.tax.id)):
                        taxes_amounts[str(item.tax.id)]["amount"] += (item.quantity * item.unit_price * item.tax.rate).quantize(Decimal('1.00'), ROUND_HALF_UP)
                    else:
                        taxes_amounts[str(item.tax.id)] = {
                            "name": item.tax.name,
                            "rate": item.tax.rate,
                            "amount": (item.quantity * item.unit_price * item.tax.rate).quantize(Decimal('1.00'), ROUND_HALF_UP)
                        }
            self._taxes_amounts = taxes_amounts.values()
        return self._taxes_amounts

    @property
    def keywords(self):
        """Genere a keywords list for the PDF headers."""
        keywords = [self.reference]
        if self.current_revision.sender:
            keywords.append(self.current_revision.sender)
        if self.contact:
            keywords.append(self.contact.get_full_name())
        if self.organization:
            keywords.append(self.organization.corporate_name)
        keywords.append("Vosae")
        return keywords

    @property
    def filename(self):
        """Return a filename based on invoice base type and reference"""
        return u'{0} {1}.pdf'.format(self.RECORD_NAME, self.reference)

    def add_revision(self, revision=None, *args, **kwargs):
        """
        Add a :class:`~invoicing.models.InvoiceRevision`.

        The :class:`~invoicing.models.InvoiceRevision` can be created with defaults
        by passing arguments.
        """
        # Retrieve the proper revision class
        document_revision = self._fields.get('current_revision').document_type

        if revision and isinstance(revision, document_revision):
            duplicate = revision.duplicate()
            if self.current_revision:
                self.revisions.insert(0, self.current_revision)
            self.current_revision = duplicate
        else:
            if self.current_revision:
                self.revisions.insert(0, self.current_revision)
            self.current_revision = document_revision(*args, **kwargs)
        return self.current_revision

    def manage_amounts(self):
        """
        Set total and amount of the :class:`~invoicing.models.Quotation`/:class:`~invoicing.models.Invoice`.

        Includes :class:`~invoicing.models.InvoiceItem`\ 's unit prices and taxes.
        """
        self.total = Decimal('0.00')
        current_revision = self.current_revision
        if current_revision:
            for line_item in current_revision.line_items:
                if line_item.optional:
                    continue
                if current_revision.taxes_application == "EXCLUSIVE":
                    self.total += Decimal(Decimal(line_item.quantity) * Decimal(line_item.unit_price) * (Decimal('1.00') + line_item.tax.rate)).quantize(Decimal('1.00'), ROUND_HALF_UP)
                elif current_revision.taxes_application == "NOT_APPLICABLE":
                    self.total += Decimal(Decimal(line_item.quantity) * Decimal(line_item.unit_price)).quantize(Decimal('1.00'), ROUND_HALF_UP)
                else:
                    continue
        self.amount = self.total

    def set_state(self, new_state, issuer=None):
        """
        Set a new state to the :class:`~invoicing.models.Quotation`/:class:`~invoicing.models.Invoice`.

        :param new_state: a state among the (:class:`~invoicing.models.Quotation`|:class:`~invoicing.models.Invoice`|:class:`~invoicing.models.DownPaymentInvoice`|:class:`~invoicing.models.CreditNote`).STATES
        :param issuer: a :class:`~core.models.VosaeUser` object to be associated to the state modification
        """
        if new_state in self.get_possible_states():
            previous_state = self.state
            self.state = new_state
            self.add_changed_state_history_entry()
            if self.state in STATES_RESET_CACHED_DATA:
                self.current_revision.pdf = None
            self.save()
            return previous_state, new_state
        else:
            try:
                raise self.InvalidState()
            except AttributeError:
                raise InvalidInvoiceBaseState("Invalid state.")

    def get_report_class(self):
        from invoicing.pdf import (
            QuotationReport,
            PurchaseOrderReport,
            InvoiceReport,
            CreditNoteReport
        )
        if self.is_quotation():
            return QuotationReport
        if self.is_purchase_order():
            return PurchaseOrderReport
        if self.is_invoice() or self.is_down_payment_invoice():
            return InvoiceReport
        if self.is_credit_note():
            return CreditNoteReport
        raise ValueError('No report class available for this type')

    def gen_pdf(self):
        """Process PDF generation based on InvoiceBaseReport"""
        buf = StringIO()
        report = self.get_report_class()(self.tenant.report_settings, self, buf)
        report.generate()
        return buf

    def get_pdf(self, issuer=None, language=None):
        """Return the cached PDF or generate and cache it."""
        from core.models import VosaeFile
        try:
            pdf_language = language or self.tenant.report_settings.language
        except:
            pdf_language = 'en'
        if not self.current_revision.pdf.get(pdf_language, None):
            with respect_language(pdf_language):
                buf = self.gen_pdf()
                pdf = ContentFile(buf.getvalue(), self.filename)
                pdf.content_type = "application/pdf"
                self.current_revision.pdf[pdf_language] = VosaeFile(
                    tenant=self.tenant,
                    uploaded_file=pdf,
                    issuer=issuer
                )
                self.current_revision.pdf[pdf_language].save()
                self.update(set__current_revision__pdf=self.current_revision.pdf)
        return self.current_revision.pdf[pdf_language]

    def send_by_mail(self, subject, message, to=[], cc=[], bcc=[], issuer=None):
        """Send the :class:`~invoicing.models.InvoiceBase` by e-mail."""
        if not self.is_issuable():
            raise NotIssuableInvoice("Invoice is not issuable.")
        context = Context({
            "reference": self.reference,
            "invoicing_date": self.current_revision.invoicing_date if self.is_invoice() and self.current_revision.invoicing_date else None,
            "signature": None
        })
        for replace, search in InvoiceBase.SENDING_VARS:
            subject = Template(subject.replace(unicode(search), replace)).render(context)
            message = Template(message.replace(unicode(search), replace)).render(context)
        pdf = self.get_pdf(issuer)
        email = EmailMessage(subject, message, to=to, cc=cc, bcc=bcc)
        email.attach(pdf.name, pdf.file.read(), pdf.content_type)
        email.send()
        self.add_sent_history_entry(method='EMAIL', to=', '.join(to))
        self.update(set__history=self.history)
