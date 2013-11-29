# -*- coding:Utf-8 -*-

from mongoengine import EmbeddedDocument, fields, ValidationError
from django.utils.timezone import now as datetime_now
import copy
import uuid

from core.fields import DateField, LocalizedMapField, NotPrivateReferenceField
from invoicing import TAXES_APPLICATION


__all__ = ('InvoiceRevision',)


class InvoiceRevision(EmbeddedDocument):

    """
    An :class:`~invoicing.models.InvoiceRevision` object is the state of the invoice
    at a specified time.

    When an invoice is updated, a revision is automatically created.
    """
    TAXES_APPLICATION = TAXES_APPLICATION

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
    quotation_date = DateField()
    quotation_validity = DateField()
    purchase_order_date = DateField()
    invoicing_date = DateField()
    due_date = DateField()
    credit_note_emission_date = DateField()
    custom_payment_conditions = fields.StringField(max_length=256)
    customer_reference = fields.StringField(max_length=128)
    currency = fields.EmbeddedDocumentField("SnapshotCurrency", required=True)
    taxes_application = fields.StringField(required=True, choices=TAXES_APPLICATION, default="EXCLUSIVE")
    line_items = fields.ListField(fields.EmbeddedDocumentField("InvoiceItem"))
    pdf = LocalizedMapField(fields.ReferenceField("VosaeFile"))

    meta = {
        # Vosae specific
        "vosae_mandatory_permissions": ("invoicing_access",),
    }

    def __unicode__(self):
        return unicode(self.revision)

    def __init__(self, *args, **kwargs):
        super(InvoiceRevision, self).__init__(*args, **kwargs)
        if not self.revision:
            self.revision = unicode(uuid.uuid4())

    def validate(self, value, **kwargs):
        errors = {}
        try:
            super(InvoiceRevision, self).validate(value, **kwargs)
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
