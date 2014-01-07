# -*- coding:Utf-8 -*-

from tastypie import http
from tastypie.utils import trailing_slash
from tastypie.exceptions import BadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.conf.urls import url

from notification.api.resources.base import NotificationBaseResource
from notification.api.resources import contacts_notifications, invoicing_notifications, organizer_notifications
from notification.models import Notification


__all__ = (
    'NotificationResource',
)


class NotificationResource(NotificationBaseResource):
    class Meta(NotificationBaseResource.Meta):
        resource_name = 'notification'
        queryset = Notification.objects.all()

        polymorphic = {
            # entity_saved
            'contact_saved_ne': contacts_notifications.ContactSavedResource,
            'organization_saved_ne': contacts_notifications.OrganizationSavedResource,

            # invoicebase_saved
            'quotation_saved_ne': invoicing_notifications.QuotationSavedResource,
            'purchase_order_saved_ne': invoicing_notifications.PurchaseOrderSavedResource,
            'invoice_saved_ne': invoicing_notifications.InvoiceSavedResource,
            'down_payment_invoice_saved_ne': invoicing_notifications.DownPaymentInvoiceSavedResource,
            'credit_note_saved_ne': invoicing_notifications.CreditNoteSavedResource,
            
            # invoicebase_changed_state
            'quotation_changed_state_ne': invoicing_notifications.QuotationChangedStateResource,
            'purchase_order_changed_state_ne': invoicing_notifications.PurchaseOrderChangedStateResource,
            'invoice_changed_state_ne': invoicing_notifications.InvoiceChangedStateResource,
            'down_payment_invoice_changed_state_ne': invoicing_notifications.DownPaymentInvoiceChangedStateResource,
            'credit_note_changed_state_ne': invoicing_notifications.CreditNoteChangedStateResource,
            
            # make_purchase_order
            'quotation_make_purchase_order_ne': invoicing_notifications.QuotationMakePurchaseOrderResource,
            
            # make_invoice
            'quotation_make_invoice_ne': invoicing_notifications.QuotationMakeInvoiceResource,
            'quotation_make_down_payment_invoice_ne': invoicing_notifications.QuotationMakeDownPaymentInvoiceResource,
            'purchase_order_make_invoice_ne': invoicing_notifications.PurchaseOrderMakeInvoiceResource,
            'purchase_order_make_down_payment_invoice_ne': invoicing_notifications.PurchaseOrderMakeDownPaymentInvoiceResource,
            
            # invoice_cancelled
            'invoice_cancelled_ne': invoicing_notifications.InvoiceCancelledResource,
            'down_payment_invoice_cancelled_ne': invoicing_notifications.DownPaymentInvoiceCancelledResource,

            # event_reminder
            'event_reminder_ne': organizer_notifications.EventReminderResource,
        }

    def prepend_urls(self):
        """Add urls for resources actions."""
        urls = super(NotificationBaseResource, self).prepend_urls()
        urls.extend((
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/mark_as_read%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('mark_as_read'), name='api_notification_mark_as_read'),
        ))
        return urls

    def mark_as_read(self, request, **kwargs):
        """Mark notification read by its recipient."""
        from invoicing.exceptions import InvalidInvoiceBaseState
        self.method_check(request, allowed=['put'])
        self.is_authenticated(request)
        self.throttle_check(request)

        try:
            bundle = self.build_bundle(request=request)
            obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()

        try:
            obj.read = True
            obj.save()
        except (obj.InvalidState, InvalidInvoiceBaseState) as e:
            raise BadRequest(e)

        self.log_throttled_access(request)

        return http.HttpNoContent()
