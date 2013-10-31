# -*- coding:Utf-8 -*-

from django.conf import settings

from vosae_utils import VosaeApiTest


class NotificationResourceTest(VosaeApiTest):

    @classmethod
    def setUpClass(cls):
        from contacts.models import Organization
        from invoicing.models import Invoice, Currency
        from notification import models as notification_models
        super(NotificationResourceTest, cls).setUpClass()

        cls.payload_kwargs = {
            'data': {},
            'HTTP_X_TENANT': settings.TENANT.slug
        }

        # Retrieve currency which will be referenced
        eur = Currency.objects.get(symbol='EUR')

        # Create an organization which will be referenced
        organization = Organization.objects.create(tenant=settings.TENANT, creator=settings.VOSAE_USER, corporate_name="My Company", private=False)

        # Create deps documents
        invoice = Invoice(
            tenant=settings.TENANT,
            account_type='RECEIVABLE',
            issuer=settings.VOSAE_USER
        )
        invoice.current_revision.currency = eur.get_snapshot()
        invoice.current_revision.organization = organization
        invoice.save()

        # Create a notification
        notification = notification_models.InvoiceChangedState()
        notification.previous_state = "DRAFT"
        notification.new_state = "REGISTERED"
        notification.issuer = settings.VOSAE_USER
        notification.recipient = settings.VOSAE_USER
        notification.tenant = settings.TENANT
        notification.invoice = invoice
        notification.save()

        cls.cached_data = {
            'invoice_uri': cls.resourceDetailURI('invoice', unicode(invoice.id)),
            'notification_uri': cls.resourceDetailURI('notification', unicode(notification.id))
        }
        cls.created_documents = [organization, notification, invoice]

    @classmethod
    def tearDownClass(cls):
        for document in cls.created_documents:
            document.delete()
        super(NotificationResourceTest, cls).tearDownClass()

    def test_01_post_list(self):
        # JSON
        response = self.api_client.client.post(self.resourceListURI('notification'), content_type='application/json; type=quotation_saved_ne', **self.payload_kwargs)
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.client.post(self.resourceListURI('notification'), content_type='application/xml; type=quotation_saved_ne', **self.payload_kwargs)
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.client.post(self.resourceListURI('notification'), content_type='application/yaml; type=quotation_saved_ne', **self.payload_kwargs)
        self.assertHttpMethodNotAllowed(response)

    def test_02_get_list(self):
        # JSON
        response = self.api_client.get(self.resourceListURI('notification'), format='json')
        self.assertValidJSONResponse(response)

        # XML
        response = self.api_client.get(self.resourceListURI('notification'), format='xml')
        self.assertValidXMLResponse(response)

        # YAML
        response = self.api_client.get(self.resourceListURI('notification'), format='yaml')
        self.assertValidYAMLResponse(response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "ItemResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(self.cached_data.get('notification_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized.get('invoice'), self.cached_data.get('invoice_uri'))
        self.assertEqual(deserialized.get('previous_state'), u"DRAFT")
        self.assertEqual(deserialized.get('new_state'), u"REGISTERED")
        self.assertEqual(deserialized.get('read'), False)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.cached_data.get('notification_uri'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.cached_data.get('notification_uri'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_04_put_list(self):
        # JSON
        response = self.api_client.put(self.resourceListURI('item'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('item'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('item'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        # JSON
        response = self.api_client.client.put(self.resourceDetailURI('notification', 'blah'), content_type='application/json; type=quotation_saved_ne', **self.payload_kwargs)
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.client.put(self.resourceDetailURI('notification', 'blah'), content_type='application/xml; type=quotation_saved_ne', **self.payload_kwargs)
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.client.put(self.resourceDetailURI('notification', 'blah'), content_type='text/yaml; type=quotation_saved_ne', **self.payload_kwargs)
        self.assertHttpMethodNotAllowed(response)

    def test_06_delete_detail(self):
        # JSON
        response = self.api_client.delete(self.resourceDetailURI('notification', 'blah'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceDetailURI('notification', 'blah'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceDetailURI('notification', 'blah'), format='yaml')
        self.assertHttpMethodNotAllowed(response)

    def test_07_delete_list(self):
        # JSON
        response = self.api_client.delete(self.resourceListURI('notification'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('notification'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('notification'), format='yaml')
        self.assertHttpMethodNotAllowed(response)
