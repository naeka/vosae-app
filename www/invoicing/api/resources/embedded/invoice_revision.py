# -*- coding:Utf-8 -*-

from django.utils.timezone import now as datetime_now
from tastypie import fields as base_fields
from tastypie_mongoengine import fields

from core.api.utils import (
    VosaeResource,
    ReferencedDictField
)
from invoicing.models import InvoiceRevision
from invoicing.api.doc import HELP_TEXT


__all__ = (
    'InvoiceRevisionResource',
)


class InvoiceRevisionResource(VosaeResource):
    revision = base_fields.CharField(
        attribute='revision',
        readonly=True,
        help_text=HELP_TEXT['invoice_revision']['revision']
    )
    issue_date = base_fields.DateTimeField(
        attribute='issue_date',
        readonly=True,
        help_text=HELP_TEXT['invoice_revision']['issue_date']
    )
    sender = base_fields.CharField(
        attribute='sender',
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoice_revision']['sender']
    )
    sender_organization = base_fields.CharField(
        attribute='sender_organization',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['invoice_revision']['sender_organization']
    )
    quotation_date = base_fields.DateField(
        attribute='quotation_date',
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoice_revision']['quotation_date']
    )
    quotation_validity = base_fields.DateField(
        attribute='quotation_validity',
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoice_revision']['quotation_validity']
    )
    purchase_order_date = base_fields.DateField(
        attribute='purchase_order_date',
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoice_revision']['purchase_order_date']
    )
    invoicing_date = base_fields.DateField(
        attribute='invoicing_date',
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoice_revision']['invoicing_date']
    )
    due_date = base_fields.DateField(
        attribute='due_date',
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoice_revision']['due_date']
    )
    credit_note_emission_date = base_fields.DateField(
        attribute='credit_note_emission_date',
        readonly=True,
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoice_revision']['credit_note_emission_date']
    )
    custom_payment_conditions = base_fields.CharField(
        attribute='custom_payment_conditions',
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoice_revision']['custom_payment_conditions']
    )
    customer_reference = base_fields.CharField(
        attribute='customer_reference',
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoice_revision']['customer_reference']
    )
    taxes_application = base_fields.CharField(
        attribute='taxes_application',
        help_text=HELP_TEXT['invoice_revision']['taxes_application']
    )

    issuer = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='issuer',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['invoice_revision']['issuer']
    )
    sender_address = fields.EmbeddedDocumentField(
        embedded='contacts.api.resources.AddressResource',
        attribute='sender_address',
        null=True,
        help_text=HELP_TEXT['invoice_revision']['sender_address']
    )
    contact = fields.ReferenceField(
        to='contacts.api.resources.ContactResource',
        attribute='contact',
        null=True,
        help_text=HELP_TEXT['invoice_revision']['contact']
    )
    organization = fields.ReferenceField(
        to='contacts.api.resources.OrganizationResource',
        attribute='organization',
        null=True,
        help_text=HELP_TEXT['invoice_revision']['organization']
    )
    billing_address = fields.EmbeddedDocumentField(
        embedded='contacts.api.resources.AddressResource',
        attribute='billing_address',
        null=True,
        help_text=HELP_TEXT['invoice_revision']['billing_address']
    )
    delivery_address = fields.EmbeddedDocumentField(
        embedded='contacts.api.resources.AddressResource',
        attribute='delivery_address',
        null=True,
        help_text=HELP_TEXT['invoice_revision']['delivery_address']
    )
    currency = fields.EmbeddedDocumentField(
        embedded='invoicing.api.resources.SnapshotCurrencyResource',
        attribute='currency',
        help_text=HELP_TEXT['invoice_revision']['currency']
    )
    line_items = fields.EmbeddedListField(
        of='invoicing.api.resources.InvoiceItemResource',
        attribute='line_items',
        full=True,
        null=True,
        help_text=HELP_TEXT['invoice_revision']['line_items']
    )
    pdf = ReferencedDictField(
        of='core.api.resources.VosaeFileResource',
        attribute='pdf',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['invoice_revision']['pdf']
    )

    class Meta(VosaeResource.Meta):
        object_class = InvoiceRevision

    def hydrate(self, bundle):
        """Set issue data and issuer on POST, extracted from request"""
        bundle = super(InvoiceRevisionResource, self).hydrate(bundle)
        bundle.obj.issuer = bundle.request.vosae_user
        bundle.obj.issue_date = datetime_now()
        return bundle
