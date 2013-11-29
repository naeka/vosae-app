# -*- coding:Utf-8 -*-

from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from tastypie import fields as base_fields, http
from tastypie.utils import trailing_slash
from tastypie.exceptions import BadRequest
from tastypie_mongoengine import fields

from core.api.utils import TenantResource, VosaeIMEXMixinResource
from invoicing.exceptions import NotDeletableInvoice, InvalidInvoiceBaseState
from invoicing import MARK_AS_STATES, INVOICE_STATES

from invoicing import imex as invoicing_imex
from invoicing import signals as invoicing_signals
from invoicing.models.embedded import invoice_history_entries
from invoicing.tasks import invoicebase_saved_task, invoicebase_changed_state_task
from invoicing.api.doc import HELP_TEXT
from core.api.resources import VosaeFileResource

from notification.mixins import NotificationAwareResourceMixin


__all__ = (
    'InvoiceBaseResource',
)


class InvoiceBaseResource(NotificationAwareResourceMixin, TenantResource, VosaeIMEXMixinResource):
    reference = base_fields.CharField(
        attribute='reference',
        readonly=True,
        help_text=HELP_TEXT['invoicebase']['reference']
    )
    total = base_fields.DecimalField(
        attribute='total',
        readonly=True,
        help_text=HELP_TEXT['invoicebase']['total']
    )
    amount = base_fields.DecimalField(
        attribute='amount',
        readonly=True,
        help_text=HELP_TEXT['invoicebase']['amount']
    )
    account_type = base_fields.CharField(
        attribute='account_type',
        help_text=HELP_TEXT['invoicebase']['account_type']
    )

    issuer = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='issuer',
        readonly=True,
        help_text=HELP_TEXT['invoicebase']['issuer']
    )
    organization = fields.ReferenceField(
        to='contacts.api.resources.OrganizationResource',
        attribute='organization',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['invoicebase']['organization']
    )
    contact = fields.ReferenceField(
        to='contacts.api.resources.ContactResource',
        attribute='contact',
        readonly=True,
        null=True,
        help_text=HELP_TEXT['invoicebase']['contact']
    )
    current_revision = fields.EmbeddedDocumentField(
        embedded='invoicing.api.resources.InvoiceRevisionResource',
        attribute='current_revision',
        help_text=HELP_TEXT['invoicebase']['current_revision']
    )
    revisions = fields.EmbeddedListField(
        of='invoicing.api.resources.InvoiceRevisionResource',
        attribute='revisions',
        readonly=True,
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoicebase']['revisions']
    )
    history = fields.EmbeddedListField(
        of='invoicing.api.resources.InvoiceHistoryEntryResource',
        attribute='history',
        readonly=True,
        full=True,
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoicebase']['history']
    )
    notes = fields.EmbeddedListField(
        of='invoicing.api.resources.InvoiceNoteResource',
        attribute='notes',
        full=True,
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoicebase']['notes']
    )
    attachments = fields.ReferencedListField(
        of='core.api.resources.VosaeFileResource',
        attribute='attachments',
        null=True,
        blank=True,
        help_text=HELP_TEXT['invoicebase']['attachments']
    )

    class Meta(TenantResource.Meta):
        excludes = ('tenant', 'base_type', 'subscribers')
        filtering = {
            'state': ('exact', 'in'),
            'contact': ('exact',),
            'organization': ('exact',),
            'account_type': ('exact',),
            'reference': ('contains',)
        }

        available_imex_serializers = (invoicing_imex.PDFSerializer,)

    def prepend_urls(self):
        """Add urls for resources actions."""
        urls = super(InvoiceBaseResource, self).prepend_urls()
        urls.extend(VosaeIMEXMixinResource.prepend_urls(self))
        urls.extend((
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/send/mail%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('send_by_mail'), name='api_invoicebase_send_by_mail'),
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/mark_as_(?P<invoicebase_state>(%s))%s$' % (self._meta.resource_name, '|'.join(
                [k.lower() for k in MARK_AS_STATES]), trailing_slash()), self.wrap_view('mark_as_state'), name='api_invoicebase_mark_as_state'),
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/generate_pdf%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('generate_pdf'), name='api_invoicebase_generate_pdf'),

        ))
        return urls

    @classmethod
    def post_save(self, sender, resource, bundle, created, **kwargs):
        """
        Post save API hook handler

        - Add timeline and notification entries
        """
        # Add timeline and notification entries
        invoicebase_saved_task.delay(bundle.request.vosae_user, bundle.obj, created)

    def obj_delete(self, bundle, **kwargs):
        """Raises a BadRequest if the :class:`~invoicing.models.InvoiceBase` is not in a deletable state"""
        try:
            super(InvoiceBaseResource, self).obj_delete(bundle, **kwargs)
        except NotDeletableInvoice as e:
            raise BadRequest(e)

    def do_export(self, request, serializer, export_objects):
        """Export"""
        if len(export_objects) is not 1:
            raise BadRequest('PDF export can only be done on a single item.')
        return serializer.serialize(export_objects[0]), None

    def send_by_mail(self, request, **kwargs):
        """Send an InvoiceBase by mail."""
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)

        try:
            bundle = self.build_bundle(request=request)
            obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()

        try:
            email_data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
            subject = email_data.get('subject')
            message = email_data.get('message')
            to = email_data.get('to')
            cc = email_data.get('cc', [])
            bcc = email_data.get('bcc', [])
            assert isinstance(to, list) and isinstance(cc, list) and isinstance(bcc, list)
        except:
            raise BadRequest('Invalid email parameters.')

        try:
            obj.send_by_mail(subject, message, to, cc, bcc, request.vosae_user)
        except:
            raise BadRequest('Can\'t send email. Verify parameters.')

        self.log_throttled_access(request)

        to_be_serialized = {}
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)

    def mark_as_state(self, request, invoicebase_state, **kwargs):
        """Set state for an InvoiceBase."""
        self.method_check(request, allowed=['put'])
        self.is_authenticated(request)
        self.throttle_check(request)

        try:
            bundle = self.build_bundle(request=request)
            obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()

        try:
            previous_state, new_state = obj.set_state(invoicebase_state.upper(), issuer=request.vosae_user)
            invoicing_signals.post_client_changed_invoice_state.send(obj.__class__, issuer=request.vosae_user, document=obj, previous_state=previous_state)
        except (obj.InvalidState, InvalidInvoiceBaseState) as e:
            raise BadRequest(e)

        self.log_throttled_access(request)

        return http.HttpNoContent()
        # May need to use this with ember (check if always_return_data)
        # to_be_serialized = ''
        # to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        # return self.create_response(request, to_be_serialized)

    def generate_pdf(self, request, **kwargs):
        """Generate a PDF"""
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        try:
            bundle = self.build_bundle(request=request)
            obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()

        try:
            language = request.META.get('HTTP_X_REPORT_LANGUAGE', None)
            if language is not None:
                assert language in [k[0] for k in settings.LANGUAGES]
        except:
            raise BadRequest('Invalid language parameters.')

        try:
            pdf = obj.get_pdf(issuer=request.vosae_user, language=language)
            pdf_resource = VosaeFileResource()
            pdf_resource_bundle = pdf_resource.build_bundle(obj=pdf, request=request)
        except:
            raise BadRequest('Can\'t generate PDF. Verify parameters.')

        self.log_throttled_access(request)

        pdf_resource_bundle = pdf_resource.full_dehydrate(pdf_resource_bundle)
        pdf_resource_bundle = pdf_resource.alter_detail_data_to_serialize(request, pdf_resource_bundle)
        return pdf_resource.create_response(request, pdf_resource_bundle)

    def full_hydrate(self, bundle):
        """
        :class:`~invoicing.models.InvoiceBase` hydratation:

        - Handle current revision immutable state if :class:`~invoicing.models.InvoiceBase` is not modifiable
        - Process some automatic affectation
        - Add history entry
        """
        # Cache original currentRevision if not modifiable
        if hasattr(bundle, 'obj') and hasattr(bundle.obj, 'is_modifiable') and not bundle.obj.is_modifiable():
            original_current_revision = getattr(bundle.obj, 'current_revision')

        # Process full_hydrate
        bundle = super(InvoiceBaseResource, self).full_hydrate(bundle)

        # Revert original currentRevision if not modifiable
        if not bundle.obj.is_modifiable():
            bundle.obj.current_revision = original_current_revision
            if 'current_revision' in bundle.obj._changed_fields:
                bundle.obj._changed_fields.remove('current_revision')

        # Process some automatic affectation
        bundle.obj.issuer = bundle.obj.current_revision.issuer
        bundle.obj.organization = bundle.obj.current_revision.organization
        bundle.obj.contact = bundle.obj.current_revision.contact

        # Add history entry
        bundle.obj.history.insert(0, invoice_history_entries.ActionHistoryEntry(
            action='UPDATED' if bundle.obj.is_created() else 'CREATED',
            issuer=bundle.obj.current_revision.issuer,
            revision=bundle.obj.current_revision.revision
        ))
        return bundle

    def hydrate(self, bundle):
        """
        If the InvoiceBase is modifiable, a new revision is added, otherwise the current_revision
        is cloned from the saved obj preventing data alteration but still allowing related updates
        such as attachments or notes.
        """
        bundle = super(InvoiceBaseResource, self).hydrate(bundle)
        if bundle.obj.is_modifiable():
            if bundle.obj.is_created():
                bundle.obj.add_revision()
            bundle.data['current_revision']['state'] = bundle.obj.state
        return bundle
