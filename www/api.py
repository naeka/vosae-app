# -*- coding:Utf-8 -*-

from tastypie.api import Api

from account.api import resources as account_resources
from core.api import resources as core_resources
from organizer.api import resources as organizer_resources
from contacts.api import resources as contacts_resources
from data_liberation.api import resources as data_liberation_resources
from invoicing.api import resources as invoicing_resources
from notification.api import resources as notification_resources
from timeline.api import resources as timeline_resources
from vosae_settings.api import resources as vosae_settings_resources
from vosae_statistics.api import resources as statistics_resources

v1_api = Api(api_name='v1')

# Account
v1_api.register(account_resources.ApiKeyResource())

# Core
v1_api.register(core_resources.TenantResource())
v1_api.register(core_resources.VosaeUserResource())
v1_api.register(core_resources.VosaeGroupResource())
v1_api.register(core_resources.VosaeFileResource())
v1_api.register(core_resources.VosaeSearchResource())

# Contacts
v1_api.register(contacts_resources.ContactResource())
v1_api.register(contacts_resources.OrganizationResource())

# Data liberation
v1_api.register(data_liberation_resources.ExportResource())

# Invoicing
v1_api.register(invoicing_resources.QuotationResource())
v1_api.register(invoicing_resources.PurchaseOrderResource())
v1_api.register(invoicing_resources.InvoiceResource())
v1_api.register(invoicing_resources.DownPaymentInvoiceResource())
v1_api.register(invoicing_resources.CreditNoteResource())
v1_api.register(invoicing_resources.PaymentResource())
v1_api.register(invoicing_resources.TaxResource())
v1_api.register(invoicing_resources.ItemResource())
v1_api.register(invoicing_resources.CurrencyResource())

# Notification
v1_api.register(notification_resources.NotificationResource())

# Organizer
v1_api.register(organizer_resources.VosaeCalendarResource())
v1_api.register(organizer_resources.CalendarListResource())
v1_api.register(organizer_resources.VosaeEventResource())

# Timeline
v1_api.register(timeline_resources.TimelineEntryResource())

# Vosae settings
v1_api.register(vosae_settings_resources.TenantSettingsResource())

# Vosae statistics
v1_api.register(statistics_resources.StatisticsResource())
