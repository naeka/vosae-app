# -*- coding:Utf-8 -*-

from mongoengine import EmbeddedDocument, fields, ValidationError
from django.utils.timezone import now as datetime_now
import copy
import uuid

from core.fields import DateField, LocalizedMapField, NotPrivateReferenceField
from invoicing import TAXES_APPLICATION


__all__ = (
    'QuotationRevision',
    'PurchaseOrderRevision',
    'InvoiceRevision',
    'CreditNoteRevision',
)


class BaseRevision(EmbeddedDocument):

    """Base class for revisions"""
    
    TAXES_APPLICATION = TAXES_APPLICATION
    NOT_DUPLICABLE_FIELDS = ('revision', 'issuer', 'issue_date', 'pdf')

    revision = fields.UUIDField(required=True, binary=True)
    issuer = fields.ReferenceField("VosaeUser")
    issue_date = fields.DateTimeField(required=True)
    sender = fields.StringField(max_length=128)
    sender_organization = fields.StringField(max_length=128)
    sender_address = fields.EmbeddedDocumentField("Address")
    contact = NotPrivateReferenceField("Contact")
    organization = NotPrivateReferenceField("Organization")
    billing_address = fields.EmbeddedDocumentField("Address")
    delivery_address = fields.EmbeddedDocumentField("Address")
    custom_payment_conditions = fields.StringField(max_length=256)
    customer_reference = fields.StringField(max_length=128)
    currency = fields.EmbeddedDocumentField("SnapshotCurrency", required=True)
    taxes_application = fields.StringField(required=True, choices=TAXES_APPLICATION, default="EXCLUSIVE")
    line_items = fields.ListField(fields.EmbeddedDocumentField("InvoiceItem"))
    pdf = LocalizedMapField(fields.ReferenceField("VosaeFile"))

    meta = {
        "allow_inheritance": True,

        # Vosae specific
        "vosae_mandatory_permissions": ("invoicing_access",),
    }

    def __unicode__(self):
        return unicode(self.revision)

    def __init__(self, *args, **kwargs):
        based_on = kwargs.pop('based_on', None)
        super(BaseRevision, self).__init__(*args, **kwargs)
        if based_on:
            # Update revision with base values
            for field in list(set(self._fields.keys()).difference(self.NOT_DUPLICABLE_FIELDS)):
                if hasattr(based_on, field):
                    setattr(self, field, getattr(based_on, field))
        if not self.revision:
            self.revision = unicode(uuid.uuid4())

    def validate(self, value, **kwargs):
        errors = {}
        try:
            super(BaseRevision, self).validate(value, **kwargs)
        except ValidationError as e:
            errors = e.errors
        if not self.contact and not self.organization:
            errors['contact'] = ValidationError('Either contact or organization is required', field_name='contact')
            errors['organization'] = ValidationError('Either contact or organization is required', field_name='organization')
        if errors:
            raise ValidationError('ValidationError', errors=errors)

    def duplicate(self, issuer=None):
        """
        Return the duplicate of the current revision with generated revision
        unique parameters.
        """
        duplicate = copy.deepcopy(self)
        duplicate.revision = unicode(uuid.uuid4())
        duplicate.issue_date = datetime_now()
        if issuer:
            duplicate.issuer = issuer
        return duplicate

    def get_customer_display(self, only_company=False):
        """
        Returns the customer's name according to this scheme:

        - Organization (Contact), *if either organization and contact are supplied*
        - Organization, *if only organization is supplied*
        - Contact, *if only contact is supplied*
        - None, *if neither organization nor contact are supplied*

        :param only_company: forces to only display the company in the first case
        """
        if self.organization and self.organization.corporate_name and self.contact and self.contact.get_full_name():
            if only_company:
                return self.organization.corporate_name
            else:
                return "%s (%s)" % (self.organization.corporate_name, self.contact.get_full_name())
        if self.organization and self.organization.corporate_name:
            return self.organization.corporate_name
        if self.contact and self.contact.get_full_name():
            return self.contact.get_full_name()
        return None


class QuotationRevision(BaseRevision):

    """
    An :class:`~invoicing.models.QuotationRevision` object is the state of the quotation
    at a specified time.

    When a quotation is updated, a revision is automatically created.
    """
    quotation_date = DateField()
    quotation_validity = DateField()


class PurchaseOrderRevision(BaseRevision):

    """
    An :class:`~invoicing.models.PurchaseOrderRevision` object is the state of a purchase order
    at a specified time.

    When a purchase order is updated, a revision is automatically created.
    """
    purchase_order_date = DateField()


class InvoiceRevision(BaseRevision):

    """
    An :class:`~invoicing.models.InvoiceRevision` object is the state of a (down-payment) invoice
    at a specified time.

    When an invoice is updated, a revision is automatically created.
    """
    invoicing_date = DateField()
    due_date = DateField()


class CreditNoteRevision(BaseRevision):

    """
    An :class:`~invoicing.models.CreditNoteRevision` object is the state of a credit note
    at a specified time.

    When a credit note is updated, a revision is automatically created.
    """
    credit_note_emission_date = DateField()