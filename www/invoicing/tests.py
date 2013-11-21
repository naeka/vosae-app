# -*- coding:Utf-8 -*-

from django.core.files.base import ContentFile
from django.conf import settings

from time import strftime
import decimal
import datetime
import copy

from vosae_utils import VosaeApiTest


tax_data = {
    "name": u"TVA",
    "rate": decimal.Decimal("0.196")
}

item_data = {
    "reference": u"ITEM1",
    "description": u"Item 1",
    "unit_price": decimal.Decimal("19.90"),
    "type": u"PRODUCT"
}

invoice_base_data = {
    "account_type": u"RECEIVABLE",
    "attachments": [],
    "current_revision":
    {
        "billing_address":
        {
            "city": u"Grenoble",
            "country": u"FRANCE",
            "extended_address": u"Level 3",
            "postal_code": u"38000",
            "street_address": u"1 Rue de Grenoble",
            "type": u"BILLING"
        },
        "delivery_address":
        {
            "city": u"Grenoble",
            "country": u"FRANCE",
            "extended_address": u"Level 3",
            "postal_code": u"38000",
            "street_address": u"1 Rue de Grenoble",
            "type": u"DELIVERY"
        },
        "sender": u"Mr. Nobody",
        "sender_address": {
            "city": u"Grenoble",
            "country": u"FRANCE",
            "postal_code": u"38000",
            "street_address": u"1 Rue de Grenoble",
            "type": u"BILLING"
        },
        "taxes_application": u"EXCLUSIVE"
    },
    "notes": [],
    "payments": []
}

quotation_data = copy.deepcopy(invoice_base_data)
quotation_data['current_revision'].update(
    quotation_date=datetime.date.today().isoformat(),
    quotation_validity=(datetime.date.today() + datetime.timedelta(days=30)).isoformat()
)
purchase_order_data = copy.deepcopy(invoice_base_data)
purchase_order_data['current_revision'].update(
    purchase_order_date=datetime.date.today().isoformat()
)
invoice_data = copy.deepcopy(invoice_base_data)
invoice_data['current_revision'].update(
    invoicing_date=datetime.date.today().isoformat(),
    due_date=(datetime.date.today() + datetime.timedelta(days=30)).isoformat()
)

down_payment_invoice_data = {
    "percentage": decimal.Decimal("0.2"),
    "due_date": (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
}

payment_data_1 = {
    "date": datetime.date.today().isoformat(),
    "amount": decimal.Decimal("10.42")
}
payment_data_2 = payment_data_1.copy()
payment_data_2 = {
    "date": datetime.date.today().isoformat(),
    "amount": decimal.Decimal("80.00")
}

expected_first_reference = strftime('%Y%m-00001')
expected_second_reference = strftime('%Y%m-00002')
expected_third_reference = strftime('%Y%m-00003')

cached_data = {}


class CurrencyResourceTest(VosaeApiTest):
    def test_01_post_list(self):
        # JSON
        response = self.api_client.post(self.resourceListURI('currency'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.post(self.resourceListURI('currency'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.post(self.resourceListURI('currency'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_02_get_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "CurrencyResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('currency'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('currency'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('currency'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_list_with_filter(self):
        # JSON
        response = self.api_client.get(self.resourceListURI('currency') + '?symbol=EUR', format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response).get('objects')), 1)
        self.assertEqual(self.deserialize(response).get('objects')[0].get('symbol'), u'EUR')
        cached_data.update(json_uri=self.deserialize(response).get('objects')[0].get('resource_uri'))

        # XML
        response = self.api_client.get(self.resourceListURI('currency') + '?symbol=EUR', format='xml')
        self.assertValidXMLResponse(response)
        deserialized_data = self.serializer.deserialize(self.api_client.replace_root_tag(response.content, 'request'), format=self.api_client.get_content_type('xml'))
        cached_data.update(xml_uri=deserialized_data[0].get('resource_uri'))

        # YAML
        response = self.api_client.get(self.resourceListURI('currency') + '?symbol=EUR', format='yaml')
        self.assertValidYAMLResponse(response)
        cached_data.update(yaml_uri=self.deserialize(response).get('objects')[0].get('resource_uri'))

    def test_04_get_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "CurrencyResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        self.assertKeys(self.deserialize(response), [u'id', u'rates', u'symbol', u'resource_uri'])
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(cached_data.get('xml_uri'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(cached_data.get('yaml_uri'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_05_put_list(self):
        # JSON
        response = self.api_client.put(self.resourceListURI('currency'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('currency'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('currency'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_06_put_detail(self):
        # JSON
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_07_delete_detail(self):
        # JSON
        response = self.api_client.delete(cached_data.get('json_uri'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(cached_data.get('xml_uri'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(cached_data.get('yaml_uri'), format='yaml')
        self.assertHttpMethodNotAllowed(response)

    def test_08_delete_list(self):
        # JSON
        response = self.api_client.delete(self.resourceListURI('currency'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('currency'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('currency'), format='yaml')
        self.assertHttpMethodNotAllowed(response)


class TaxResourceTest(VosaeApiTest):
    def test_01_post_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "TaxResource", "method": "post_list", "serializer": "json"}
        response = self.api_client.post(self.resourceListURI('tax'), format='json', data=tax_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.post(self.resourceListURI('tax'), format='xml', data=tax_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.post(self.resourceListURI('tax'), format='yaml', data=tax_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "TaxResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('tax'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('tax'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('tax'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "TaxResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(self.deserialize(response).get('name'), u'TVA')
        self.assertEqual(self.deserialize(response).get('rate'), u'0.1960')
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(cached_data.get('xml_uri'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(cached_data.get('yaml_uri'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_04_put_list(self):
        # JSON
        response = self.api_client.put(self.resourceListURI('tax'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('tax'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('tax'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        tax_data.update(name=u"TVA 19.6")
        # JSON
        infos = {"app": "invoicing", "resource": "TaxResource", "method": "put_detail", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=tax_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=tax_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=tax_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_delete_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "TaxResource", "method": "delete_detail", "serializer": "json"}
        response = self.api_client.delete(cached_data.get('json_uri'), format='json')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertIn('status', deserialized)
        self.assertEqual('INACTIVE', deserialized.get('status'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.delete(cached_data.get('xml_uri'), format='xml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('xml_uri'), format='xml')
        self.assertValidXMLResponse(response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.delete(cached_data.get('yaml_uri'), format='yaml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('yaml_uri'), format='yaml')
        self.assertValidYAMLResponse(response)

    def test_07_delete_list(self):
        # JSON
        response = self.api_client.delete(self.resourceListURI('tax'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('tax'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('tax'), format='yaml')
        self.assertHttpMethodNotAllowed(response)

    def test_08_repost_inactive(self):
        # JSON
        # No uniqueness constraint with taxes, repost should be accepted
        response = self.api_client.post(self.resourceListURI('tax'), format='json', data=tax_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)


class ItemResourceTest(VosaeApiTest):
    @classmethod
    def setUpClass(cls):
        from invoicing.models import Currency, Tax
        super(ItemResourceTest, cls).setUpClass()
        # Retrieve currency which will be referenced
        eur = Currency.objects.get(symbol='EUR')

        # Create tax which will be referenced
        new_tax_data = tax_data.copy()
        new_tax_data.update(tenant=settings.TENANT)
        new_tax = Tax(**new_tax_data)
        new_tax.save()

        # Set them to item data
        item_data.update(
            currency=cls.resourceDetailURI('currency', unicode(eur.id)),
            tax=cls.resourceDetailURI('tax', unicode(new_tax.id)),
        )

        cls.created_documents = [new_tax]

    @classmethod
    def tearDownClass(cls):
        for document in cls.created_documents:
            document.delete()
        super(ItemResourceTest, cls).tearDownClass()

    def test_01_post_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "ItemResource", "method": "post_list", "serializer": "json"}
        response = self.api_client.post(self.resourceListURI('item'), format='json', data=item_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))

        # XML
        infos.update(serializer='xml')
        item_data.update(reference=u'ITEM2', description=u'Item 2')
        response = self.api_client.post(self.resourceListURI('item'), format='xml', data=item_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        item_data.update(reference=u'ITEM3', description=u'Item 3')
        response = self.api_client.post(self.resourceListURI('item'), format='yaml', data=item_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "ItemResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('item'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('item'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('item'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "ItemResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(self.deserialize(response).get('reference'), u'ITEM1')
        self.assertEqual(self.deserialize(response).get('unit_price'), u'19.90')
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(cached_data.get('xml_uri'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(cached_data.get('yaml_uri'), format='yaml')
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
        infos = {"app": "invoicing", "resource": "ItemResource", "method": "put_detail", "serializer": "json"}
        item_data.update(reference=u"ITEM-A", description=u'Item A')
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=item_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(self.deserialize(response).get('reference'), u'ITEM-A')
        self.assertEqual(self.deserialize(response).get('description'), u'Item A')

        # XML
        infos.update(serializer='xml')
        item_data.update(reference=u'ITEM-B', description=u'Item B')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=item_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        item_data.update(reference=u'ITEM-C', description=u'Item C')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=item_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_delete_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "ItemResource", "method": "delete_detail", "serializer": "json"}
        response = self.api_client.delete(cached_data.get('json_uri'), format='json')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertIn('status', deserialized)
        self.assertEqual('INACTIVE', deserialized.get('status'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.delete(cached_data.get('xml_uri'), format='xml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('xml_uri'), format='xml')
        self.assertValidXMLResponse(response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.delete(cached_data.get('yaml_uri'), format='yaml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('yaml_uri'), format='yaml')
        self.assertValidYAMLResponse(response)

    def test_07_delete_list(self):
        # JSON
        response = self.api_client.delete(self.resourceListURI('item'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('item'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('item'), format='yaml')
        self.assertHttpMethodNotAllowed(response)

    def test_08_repost_inactive(self):
        # JSON
        response = self.api_client.post(self.resourceListURI('item'), format='json', data=item_data)
        self.assertHttpConflict(response)
        self.assertEqual(response.content, 'A document with this reference already exists. It can be waked up thanks to the X-WakeUp header (if in a DELETED/INACTIVE status)  or you can set different values')

        response = self.api_client.post(self.resourceListURI('item'), format='json', data=item_data, HTTP_X_WAKEUP='ACTIVE')
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)


class InvoiceBaseResourceTest(VosaeApiTest):
    @classmethod
    def setUpClass(cls):
        from contacts.models import Organization, Contact
        from invoicing.models import Currency, Tax, Item
        from vosae_utils import VosaeTestApiClient
        from tastypie.serializers import Serializer
        super(InvoiceBaseResourceTest, cls).setUpClass()
        api_client = VosaeTestApiClient()
        api_client.client.login(email='nobody@vosae.com', password='password')
        serializer = Serializer()

        # Retrieve currency which will be referenced
        eur = Currency.objects.get(symbol='EUR')

        # Create tax which will be referenced
        new_tax_data = tax_data.copy()
        new_tax_data.update(tenant=settings.TENANT)
        new_tax = Tax(**new_tax_data)
        new_tax.save()

        # Create an organization which will be referenced
        organization = Organization.objects.create(tenant=settings.TENANT, creator=settings.VOSAE_USER, corporate_name="My Company", private=False)

        # Create a contact, linked to the organization, which will be referenced
        contact = Contact.objects.create(tenant=settings.TENANT, creator=settings.VOSAE_USER, name='Name', firstname='Firstname', organization=organization, private=False)

        # Create an item which will be referenced
        new_item_data = item_data.copy()
        new_item_data.update(
            reference='ITEM1',
            description='Item 1',
            tenant=settings.TENANT,
            currency=eur,
            tax=new_tax
        )
        item = Item.objects.create(**new_item_data)

        # Get currency JSON
        response = api_client.get(cls.resourceDetailURI('currency', unicode(eur.id)), format='json')
        deserialized_currency = serializer.deserialize(response.content, format='application/json')

        # Set line item data
        line_item = new_item_data.copy()
        line_item.update(
            item_id=unicode(item.id),
            quantity=decimal.Decimal("2"),
            tax=cls.resourceDetailURI('tax', unicode(new_tax.id))
        )
        del line_item["currency"]
        del line_item["tenant"]

        # Set them to quotation data
        quotation_data["current_revision"].update(
            contact=cls.resourceDetailURI('contact', unicode(contact.id)),
            organization=cls.resourceDetailURI('organization', unicode(organization.id)),
            currency=deserialized_currency,
            line_items=[line_item],
        )

        # Set them to purchase order data
        purchase_order_data["current_revision"].update(
            contact=cls.resourceDetailURI('contact', unicode(contact.id)),
            organization=cls.resourceDetailURI('organization', unicode(organization.id)),
            currency=deserialized_currency,
            line_items=[line_item],
        )

        # Set the invoice data
        invoice_data["current_revision"].update(
            contact=cls.resourceDetailURI('contact', unicode(contact.id)),
            organization=cls.resourceDetailURI('organization', unicode(organization.id)),
            currency=deserialized_currency,
            line_items=[line_item],
        )

        # Set currency to payments
        payment_data_1.update(currency=cls.resourceDetailURI('currency', unicode(eur.id)))
        payment_data_2.update(currency=cls.resourceDetailURI('currency', unicode(eur.id)))

        # Set tax to down payment invoice data
        down_payment_invoice_data.update(tax_applied=cls.resourceDetailURI('tax', unicode(new_tax.id)))

        cls.created_documents = [new_tax, organization, contact, item]

    @classmethod
    def tearDownClass(cls):
        from invoicing.models import Item
        for document in cls.created_documents:
            if isinstance(document, Item):
                document.delete(force=True)
            else:
                document.delete()
        super(InvoiceBaseResourceTest, cls).tearDownClass()


class QuotationResourceTest(InvoiceBaseResourceTest):
    @classmethod
    def setUpClass(cls):
        from core.models import VosaeFile
        super(QuotationResourceTest, cls).setUpClass()
        attachment_1 = VosaeFile(tenant=settings.TENANT, uploaded_file=ContentFile('Attachment 1', name='test file.txt')).save()
        attachment_2 = VosaeFile(tenant=settings.TENANT, uploaded_file=ContentFile('Attachment 2', name='test file.txt')).save()
        cls.cached_data = {
            'attachment_1_uri': cls.resourceDetailURI('file', unicode(attachment_1.id)),
            'attachment_2_uri': cls.resourceDetailURI('file', unicode(attachment_2.id))
        }
        cls.created_documents += [attachment_1, attachment_2]

    @classmethod
    def tearDownClass(cls):
        quotation_data['attachments'] = []
        super(QuotationResourceTest, cls).tearDownClass()

    def test_01_post_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "QuotationResource", "method": "post_list", "serializer": "json"}
        response = self.api_client.post(self.resourceListURI('quotation'), format='json', data=quotation_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))
        # For later use
        response = self.api_client.post(self.resourceListURI('quotation'), format='json', data=quotation_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        cached_data.update(json_uri2=response.get('location'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.post(self.resourceListURI('quotation'), format='xml', data=quotation_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))
        # For later use
        response = self.api_client.post(self.resourceListURI('quotation'), format='xml', data=quotation_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        cached_data.update(xml_uri2=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.post(self.resourceListURI('quotation'), format='yaml', data=quotation_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))
        # For later use
        response = self.api_client.post(self.resourceListURI('quotation'), format='yaml', data=quotation_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        cached_data.update(yaml_uri2=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "QuotationResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('quotation'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('quotation'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('quotation'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "QuotationResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 0)
        self.assertEqual(deserialized['current_revision']['delivery_address']['city'], u'Grenoble')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'ITEM1')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'19.90')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'2.00')
        self.assertEqual(deserialized['amount'], u'47.60')
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(cached_data.get('xml_uri'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(cached_data.get('yaml_uri'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_04_put_list(self):
        # JSON
        response = self.api_client.put(self.resourceListURI('quotation'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('quotation'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('quotation'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        quotation_data['current_revision']['line_items'][0]['quantity'] = decimal.Decimal("4")
        quotation_data['current_revision']['line_items'][0]['unit_price'] = decimal.Decimal("18.90")
        # JSON
        infos = {"app": "invoicing", "resource": "QuotationResource", "method": "put_detail", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=quotation_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 1)
        self.assertEqual(deserialized['current_revision']['delivery_address']['city'], u'Grenoble')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'ITEM1')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'18.90')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'4.00')
        self.assertEqual(deserialized['amount'], u'90.42')

        response = self.api_client.get(deserialized['revisions'][0], format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['line_items'][0]['quantity'], u'2.00')
        self.assertEqual(deserialized['line_items'][0]['unit_price'], u'19.90')

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=quotation_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=quotation_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_add_attachment(self):
        file_data = {
            'uploaded_file': ContentFile('Test file', name='test file.txt')
        }

        # Post a file
        response = self.api_client.post(self.resourceListURI('file'), format='json', data=file_data, disposition='form-data')
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        file_uri = self.fullURItoAbsoluteURI(response.get('location'))

        # Add file to attachments
        quotation_data['attachments'].append(file_uri)

        # JSON
        infos = {"app": "invoicing", "resource": "QuotationResource", "method": "add_attachment", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=quotation_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Check attachment presence
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['attachments']), 1)

        # Delete attachment
        quotation_data['attachments'].remove(file_uri)
        response = self.api_client.delete(deserialized['attachments'][0], format='json')
        self.assertHttpAccepted(response)
        response = self.api_client.get(deserialized['attachments'][0], format='json')
        self.assertHttpNotFound(response)

        # Check that attachment is no more listed
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['attachments']), 0)

        # Add attachment for other serializers
        quotation_data['attachments'].append(self.cached_data.get('attachment_1_uri'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=quotation_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=quotation_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_07_mark_as_awaiting_approval(self):
        # JSON
        infos = {"app": "invoicing", "resource": "QuotationResource", "method": "mark_as_awaiting_approval", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri') + 'mark_as_awaiting_approval/', format='json')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)

        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['state'], "AWAITING_APPROVAL")

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri') + 'mark_as_awaiting_approval/', format='xml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri') + 'mark_as_awaiting_approval/', format='yaml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)

        # Check that other methods are not allowed
        response = self.api_client.post(cached_data.get('json_uri') + 'mark_as_awaiting_approval/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.get(cached_data.get('json_uri') + 'mark_as_awaiting_approval/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.delete(cached_data.get('json_uri') + 'mark_as_awaiting_approval/', format='json')
        self.assertHttpMethodNotAllowed(response)

    def test_08_make_purchase_order(self):
        # JSON
        infos = {"app": "invoicing", "resource": "QuotationResource", "method": "make_purchase_order", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri') + 'make_purchase_order/', format='json')
        self.assertHttpOK(response)
        deserialized = self.deserialize(response)
        self.save_test_result(infos, response)

        response = self.api_client.get(deserialized.get('purchase_order_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 0)
        self.assertEqual(deserialized['current_revision']['delivery_address']['city'], u'Grenoble')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'ITEM1')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['description'], u'Item 1')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'18.90')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'4.00')
        self.assertEqual(deserialized['amount'], u'90.42')

        # Check that references are present
        response = self.api_client.get(deserialized['group']['quotation'], format='json')
        self.assertValidJSONResponse(response)
        deserialized_quotation = self.deserialize(response)
        self.assertEqual(deserialized_quotation['state'], u'AWAITING_APPROVAL')
        self.assertEqual(deserialized_quotation['group']['purchase_order'], deserialized.get('resource_uri'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri') + 'make_purchase_order/', format='xml')
        self.assertHttpOK(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri') + 'make_purchase_order/', format='yaml')
        self.assertHttpOK(response)
        self.save_test_result(infos, response)

        # Check that other methods are not allowed
        response = self.api_client.post(cached_data.get('json_uri') + 'make_purchase_order/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.get(cached_data.get('json_uri') + 'make_purchase_order/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.delete(cached_data.get('json_uri') + 'make_purchase_order/', format='json')
        self.assertHttpMethodNotAllowed(response)

    def test_09_make_down_payment_invoice(self):
        # JSON
        infos = {"app": "invoicing", "resource": "QuotationResource", "method": "make_down_payment_invoice", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri') + 'make_down_payment_invoice/', format='json', data=down_payment_invoice_data)
        self.assertHttpOK(response)
        deserialized = self.deserialize(response)
        self.save_test_result(infos, response)

        response = self.api_client.get(deserialized.get('down_payment_invoice_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 0)
        self.assertEqual(deserialized['current_revision']['delivery_address']['city'], u'Grenoble')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'DOWN-PAYMENT')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['description'], u'20%% down-payment on quotation %s' % expected_third_reference)
        self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'15.12')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'1.00')
        self.assertEqual(deserialized['amount'], u'18.08')

        # Check down_payment presence
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['group']['down_payment_invoices']), 1)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri') + 'make_down_payment_invoice/', format='xml', data=down_payment_invoice_data)
        self.assertHttpOK(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri') + 'make_down_payment_invoice/', format='yaml', data=down_payment_invoice_data)
        self.assertHttpOK(response)
        self.save_test_result(infos, response)

        # Check that other methods are not allowed
        response = self.api_client.post(cached_data.get('json_uri') + 'make_down_payment_invoice/', format='json', data=down_payment_invoice_data)
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.get(cached_data.get('json_uri') + 'make_down_payment_invoice/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.delete(cached_data.get('json_uri') + 'make_down_payment_invoice/', format='json')
        self.assertHttpMethodNotAllowed(response)

    def test_10_make_invoice(self):
        # JSON
        infos = {"app": "invoicing", "resource": "QuotationResource", "method": "make_invoice", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri') + 'make_invoice/', format='json')
        self.assertHttpOK(response)
        deserialized = self.deserialize(response)
        self.save_test_result(infos, response)

        response = self.api_client.get(deserialized.get('invoice_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 0)
        self.assertEqual(deserialized['current_revision']['delivery_address']['city'], u'Grenoble')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'ITEM1')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['description'], u'Item 1')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'18.90')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'4.00')
        self.assertEqual(deserialized['amount'], u'72.34')

        # Check that references are present
        response = self.api_client.get(deserialized['group']['quotation'], format='json')
        self.assertValidJSONResponse(response)
        deserialized_quotation = self.deserialize(response)
        self.assertEqual(deserialized_quotation['state'], u'INVOICED')
        self.assertEqual(deserialized_quotation['group']['invoice'], deserialized.get('resource_uri'))
        self.assertEqual(len(deserialized_quotation['group']['down_payment_invoices']), 1)

        # Check that state is updated if invoice is deleted
        response = self.api_client.delete(deserialized.get('resource_uri'), format='json')
        self.assertHttpAccepted(response)
        response = self.api_client.get(deserialized['group']['quotation'], format='json')
        self.assertValidJSONResponse(response)
        deserialized_quotation = self.deserialize(response)
        self.assertEqual(deserialized_quotation['state'], u'APPROVED')
        self.assertEqual(deserialized_quotation['group']['invoice'], None)
        self.assertEqual(len(deserialized_quotation['group']['down_payment_invoices']), 1)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri') + 'make_invoice/', format='xml')
        self.assertHttpOK(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri') + 'make_invoice/', format='yaml')
        self.assertHttpOK(response)
        self.save_test_result(infos, response)

        # Check that other methods are not allowed
        response = self.api_client.post(cached_data.get('json_uri') + 'make_invoice/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.get(cached_data.get('json_uri') + 'make_invoice/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.delete(cached_data.get('json_uri') + 'make_invoice/', format='json')
        self.assertHttpMethodNotAllowed(response)

    def test_11_delete_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "QuotationResource", "method": "delete_detail", "serializer": "json"}
        response = self.api_client.delete(cached_data.get('json_uri'), format='json')
        self.assertHttpBadRequest(response)  # Not in a deletable state (linked to [DownPayment]Invoices)
        response = self.api_client.delete(cached_data.get('json_uri2'), format='json')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('json_uri2'), format='json')
        self.assertHttpNotFound(response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.delete(cached_data.get('xml_uri'), format='xml')
        self.assertHttpBadRequest(response)  # Not in a deletable state (linked to [DownPayment]Invoices)
        response = self.api_client.delete(cached_data.get('xml_uri2'), format='xml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('xml_uri2'), format='xml')
        self.assertHttpNotFound(response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.delete(cached_data.get('yaml_uri'), format='yaml')
        self.assertHttpBadRequest(response)  # Not in a deletable state (linked to [DownPayment]Invoices)
        response = self.api_client.delete(cached_data.get('yaml_uri2'), format='yaml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('yaml_uri2'), format='yaml')
        self.assertHttpNotFound(response)

    def test_12_delete_list(self):
        # JSON
        response = self.api_client.delete(self.resourceListURI('quotation'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('quotation'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('quotation'), format='yaml')
        self.assertHttpMethodNotAllowed(response)


class PurchaseOrderResourceTest(InvoiceBaseResourceTest):
    @classmethod
    def setUpClass(cls):
        from core.models import VosaeFile
        super(PurchaseOrderResourceTest, cls).setUpClass()
        attachment_1 = VosaeFile(tenant=settings.TENANT, uploaded_file=ContentFile('Attachment 1', name='test file.txt')).save()
        attachment_2 = VosaeFile(tenant=settings.TENANT, uploaded_file=ContentFile('Attachment 2', name='test file.txt')).save()
        cls.cached_data = {
            'attachment_1_uri': cls.resourceDetailURI('file', unicode(attachment_1.id)),
            'attachment_2_uri': cls.resourceDetailURI('file', unicode(attachment_2.id))
        }
        cls.created_documents += [attachment_1, attachment_2]

    @classmethod
    def tearDownClass(cls):
        purchase_order_data['attachments'] = []
        super(PurchaseOrderResourceTest, cls).tearDownClass()

    def test_01_post_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "PurchaseOrderResource", "method": "post_list", "serializer": "json"}
        response = self.api_client.post(self.resourceListURI('purchase_order'), format='json', data=purchase_order_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))
        # For later use
        response = self.api_client.post(self.resourceListURI('purchase_order'), format='json', data=purchase_order_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        cached_data.update(json_uri2=response.get('location'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.post(self.resourceListURI('purchase_order'), format='xml', data=purchase_order_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))
        # For later use
        response = self.api_client.post(self.resourceListURI('purchase_order'), format='xml', data=purchase_order_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        cached_data.update(xml_uri2=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.post(self.resourceListURI('purchase_order'), format='yaml', data=purchase_order_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))
        # For later use
        response = self.api_client.post(self.resourceListURI('purchase_order'), format='yaml', data=purchase_order_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        cached_data.update(yaml_uri2=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "PurchaseOrderResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('purchase_order'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('purchase_order'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('purchase_order'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "PurchaseOrderResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 0)
        self.assertEqual(deserialized['current_revision']['delivery_address']['city'], u'Grenoble')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'ITEM1')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'19.90')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'2.00')
        self.assertEqual(deserialized['amount'], u'47.60')
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(cached_data.get('xml_uri'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(cached_data.get('yaml_uri'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_04_put_list(self):
        # JSON
        response = self.api_client.put(self.resourceListURI('purchase_order'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('purchase_order'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('purchase_order'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        purchase_order_data['current_revision']['line_items'][0]['quantity'] = decimal.Decimal("4")
        purchase_order_data['current_revision']['line_items'][0]['unit_price'] = decimal.Decimal("18.90")
        # JSON
        infos = {"app": "invoicing", "resource": "PurchaseOrderResource", "method": "put_detail", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=purchase_order_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 1)
        self.assertEqual(deserialized['current_revision']['delivery_address']['city'], u'Grenoble')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'ITEM1')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'18.90')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'4.00')
        self.assertEqual(deserialized['amount'], u'90.42')

        response = self.api_client.get(deserialized['revisions'][0], format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['line_items'][0]['quantity'], u'2.00')
        self.assertEqual(deserialized['line_items'][0]['unit_price'], u'19.90')

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=purchase_order_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=purchase_order_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_add_attachment(self):
        file_data = {
            'uploaded_file': ContentFile('Test file', name='test file.txt')
        }

        # Post a file
        response = self.api_client.post(self.resourceListURI('file'), format='json', data=file_data, disposition='form-data')
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        file_uri = self.fullURItoAbsoluteURI(response.get('location'))

        # Add file to attachments
        purchase_order_data['attachments'].append(file_uri)

        # JSON
        infos = {"app": "invoicing", "resource": "PurchaseOrderResource", "method": "add_attachment", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=purchase_order_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Check attachment presence
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['attachments']), 1)

        # Delete attachment
        purchase_order_data['attachments'].remove(file_uri)
        response = self.api_client.delete(deserialized['attachments'][0], format='json')
        self.assertHttpAccepted(response)
        response = self.api_client.get(deserialized['attachments'][0], format='json')
        self.assertHttpNotFound(response)

        # Check that attachment is no more listed
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['attachments']), 0)

        # Add attachment for other serializers
        purchase_order_data['attachments'].append(self.cached_data.get('attachment_1_uri'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=purchase_order_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=purchase_order_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_07_mark_as_awaiting_approval(self):
        # JSON
        infos = {"app": "invoicing", "resource": "PurchaseOrderResource", "method": "mark_as_awaiting_approval", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri') + 'mark_as_awaiting_approval/', format='json')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)

        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['state'], "AWAITING_APPROVAL")

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri') + 'mark_as_awaiting_approval/', format='xml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri') + 'mark_as_awaiting_approval/', format='yaml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)

        # Check that other methods are not allowed
        response = self.api_client.post(cached_data.get('json_uri') + 'mark_as_awaiting_approval/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.get(cached_data.get('json_uri') + 'mark_as_awaiting_approval/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.delete(cached_data.get('json_uri') + 'mark_as_awaiting_approval/', format='json')
        self.assertHttpMethodNotAllowed(response)

    def test_08_make_down_payment_invoice(self):
        # JSON
        infos = {"app": "invoicing", "resource": "PurchaseOrderResource", "method": "make_down_payment_invoice", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri') + 'make_down_payment_invoice/', format='json', data=down_payment_invoice_data)
        self.assertHttpOK(response)
        deserialized = self.deserialize(response)
        self.save_test_result(infos, response)

        response = self.api_client.get(deserialized.get('down_payment_invoice_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 0)
        self.assertEqual(deserialized['current_revision']['delivery_address']['city'], u'Grenoble')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'DOWN-PAYMENT')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['description'], u'20%% down-payment on purchase order %s' % expected_first_reference)
        self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'15.12')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'1.00')
        self.assertEqual(deserialized['amount'], u'18.08')

        # Check down_payment presence
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['group']['down_payment_invoices']), 1)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri') + 'make_down_payment_invoice/', format='xml', data=down_payment_invoice_data)
        self.assertHttpOK(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri') + 'make_down_payment_invoice/', format='yaml', data=down_payment_invoice_data)
        self.assertHttpOK(response)
        self.save_test_result(infos, response)

        # Check that other methods are not allowed
        response = self.api_client.post(cached_data.get('json_uri') + 'make_down_payment_invoice/', format='json', data=down_payment_invoice_data)
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.get(cached_data.get('json_uri') + 'make_down_payment_invoice/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.delete(cached_data.get('json_uri') + 'make_down_payment_invoice/', format='json')
        self.assertHttpMethodNotAllowed(response)

    def test_09_make_invoice(self):
        # JSON
        infos = {"app": "invoicing", "resource": "PurchaseOrderResource", "method": "make_invoice", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri') + 'make_invoice/', format='json')
        self.assertHttpOK(response)
        deserialized = self.deserialize(response)
        self.save_test_result(infos, response)

        response = self.api_client.get(deserialized.get('invoice_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 0)
        self.assertEqual(deserialized['current_revision']['delivery_address']['city'], u'Grenoble')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'ITEM1')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['description'], u'Item 1')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'18.90')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'4.00')
        self.assertEqual(deserialized['amount'], u'72.34')

        # Check that references are present
        response = self.api_client.get(deserialized['group']['purchase_order'], format='json')
        self.assertValidJSONResponse(response)
        deserialized_purchase_order = self.deserialize(response)
        self.assertEqual(deserialized_purchase_order['state'], u'INVOICED')
        self.assertEqual(deserialized_purchase_order['group']['invoice'], deserialized.get('resource_uri'))
        self.assertEqual(len(deserialized_purchase_order['group']['down_payment_invoices']), 1)

        # Check that state is updated if invoice is deleted
        response = self.api_client.delete(deserialized.get('resource_uri'), format='json')
        self.assertHttpAccepted(response)
        response = self.api_client.get(deserialized['group']['purchase_order'], format='json')
        self.assertValidJSONResponse(response)
        deserialized_purchase_order = self.deserialize(response)
        self.assertEqual(deserialized_purchase_order['state'], u'APPROVED')
        self.assertEqual(deserialized_purchase_order['group']['invoice'], None)
        self.assertEqual(len(deserialized_purchase_order['group']['down_payment_invoices']), 1)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri') + 'make_invoice/', format='xml')
        self.assertHttpOK(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri') + 'make_invoice/', format='yaml')
        self.assertHttpOK(response)
        self.save_test_result(infos, response)

        # Check that other methods are not allowed
        response = self.api_client.post(cached_data.get('json_uri') + 'make_invoice/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.get(cached_data.get('json_uri') + 'make_invoice/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.delete(cached_data.get('json_uri') + 'make_invoice/', format='json')
        self.assertHttpMethodNotAllowed(response)

    def test_10_delete_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "PurchaseOrderResource", "method": "delete_detail", "serializer": "json"}
        response = self.api_client.delete(cached_data.get('json_uri'), format='json')
        self.assertHttpBadRequest(response)  # Not in a deletable state (linked to [DownPayment]Invoices)
        response = self.api_client.delete(cached_data.get('json_uri2'), format='json')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('json_uri2'), format='json')
        self.assertHttpNotFound(response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.delete(cached_data.get('xml_uri'), format='xml')
        self.assertHttpBadRequest(response)  # Not in a deletable state (linked to [DownPayment]Invoices)
        response = self.api_client.delete(cached_data.get('xml_uri2'), format='xml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('xml_uri2'), format='xml')
        self.assertHttpNotFound(response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.delete(cached_data.get('yaml_uri'), format='yaml')
        self.assertHttpBadRequest(response)  # Not in a deletable state (linked to [DownPayment]Invoices)
        response = self.api_client.delete(cached_data.get('yaml_uri2'), format='yaml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('yaml_uri2'), format='yaml')
        self.assertHttpNotFound(response)

    def test_11_delete_list(self):
        # JSON
        response = self.api_client.delete(self.resourceListURI('purchase_order'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('purchase_order'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('purchase_order'), format='yaml')
        self.assertHttpMethodNotAllowed(response)


class InvoiceResourceTest(InvoiceBaseResourceTest):
    @classmethod
    def setUpClass(cls):
        from core.models import VosaeFile
        super(InvoiceResourceTest, cls).setUpClass()
        attachment_1 = VosaeFile(tenant=settings.TENANT, uploaded_file=ContentFile('Attachment 1', name='test file.txt')).save()
        attachment_2 = VosaeFile(tenant=settings.TENANT, uploaded_file=ContentFile('Attachment 2', name='test file.txt')).save()
        cls.cached_data = {
            'attachment_1_uri': cls.resourceDetailURI('file', unicode(attachment_1.id)),
            'attachment_2_uri': cls.resourceDetailURI('file', unicode(attachment_2.id))
        }
        cls.created_documents += [attachment_1, attachment_2]

    @classmethod
    def tearDownClass(cls):
        invoice_data['attachments'] = []
        super(InvoiceResourceTest, cls).tearDownClass()

    def test_01_post_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "InvoiceResource", "method": "post_list", "serializer": "json"}
        response = self.api_client.post(self.resourceListURI('invoice'), format='json', data=invoice_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))
        # For later use
        response = self.api_client.post(self.resourceListURI('invoice'), format='json', data=invoice_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        cached_data.update(json_uri2=response.get('location'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.post(self.resourceListURI('invoice'), format='xml', data=invoice_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))
        # For later use
        response = self.api_client.post(self.resourceListURI('invoice'), format='xml', data=invoice_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        cached_data.update(xml_uri2=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.post(self.resourceListURI('invoice'), format='yaml', data=invoice_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))
        # For later use
        response = self.api_client.post(self.resourceListURI('invoice'), format='yaml', data=invoice_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        cached_data.update(yaml_uri2=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "InvoiceResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('invoice'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('invoice'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('invoice'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "InvoiceResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 0)
        self.assertEqual(deserialized['current_revision']['delivery_address']['city'], u'Grenoble')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'ITEM1')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'19.90')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'2.00')
        self.assertEqual(deserialized['amount'], u'47.60')
        self.assertEqual(len(deserialized.get('history')), 1)
        self.assertEqual(deserialized.get('history')[0].get('resource_type'), 'action_history_entry')
        self.assertEqual(deserialized.get('history')[0].get('action'), 'CREATED')
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(cached_data.get('xml_uri'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(cached_data.get('yaml_uri'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_04_put_list(self):
        # JSON
        response = self.api_client.put(self.resourceListURI('invoice'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('invoice'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('invoice'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        invoice_data['current_revision']['line_items'][0]['quantity'] = decimal.Decimal("4")
        invoice_data['current_revision']['line_items'][0]['unit_price'] = decimal.Decimal("18.90")
        # JSON
        infos = {"app": "invoicing", "resource": "InvoiceResource", "method": "put_detail", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=invoice_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 1)
        self.assertEqual(deserialized['current_revision']['delivery_address']['city'], u'Grenoble')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'ITEM1')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'18.90')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'4.00')
        self.assertEqual(deserialized['amount'], u'90.42')
        self.assertEqual(len(deserialized.get('history')), 2)
        self.assertEqual(deserialized.get('history')[0].get('resource_type'), 'action_history_entry')
        self.assertEqual(deserialized.get('history')[0].get('action'), 'UPDATED')

        response = self.api_client.get(deserialized['revisions'][0], format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['line_items'][0]['quantity'], u'2.00')
        self.assertEqual(deserialized['line_items'][0]['unit_price'], u'19.90')

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=invoice_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=invoice_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_add_attachment(self):
        file_data = {
            'uploaded_file': ContentFile('Test file', name='test file.txt')
        }

        # Post a file
        response = self.api_client.post(self.resourceListURI('file'), format='json', data=file_data, disposition='form-data')
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        file_uri = self.fullURItoAbsoluteURI(response.get('location'))

        # Add file to attachments
        invoice_data['attachments'].append(file_uri)

        # JSON
        infos = {"app": "invoicing", "resource": "InvoiceResource", "method": "add_attachment", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=invoice_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Check PUT and attachment presence
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['revisions']), 2)
        self.assertEqual(len(deserialized['attachments']), 1)

        # Delete attachment
        invoice_data['attachments'].remove(file_uri)
        response = self.api_client.delete(deserialized['attachments'][0], format='json')
        self.assertHttpAccepted(response)
        response = self.api_client.get(deserialized['attachments'][0], format='json')
        self.assertHttpNotFound(response)

        # Check that attachment is no more listed
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['attachments']), 0)

        # Add attachment for other serializers
        invoice_data['attachments'].append(self.cached_data.get('attachment_1_uri'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=invoice_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=invoice_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_07_cancel_impossible_on_draft(self):
        # JSON
        response = self.api_client.put(cached_data.get('json_uri') + 'cancel/', format='json')
        self.assertHttpBadRequest(response)

        # XML
        response = self.api_client.put(cached_data.get('xml_uri') + 'cancel/', format='xml')
        self.assertHttpBadRequest(response)

        # YAML
        response = self.api_client.put(cached_data.get('yaml_uri') + 'cancel/', format='yaml')
        self.assertHttpBadRequest(response)

        # Check that other methods are not allowed
        response = self.api_client.post(cached_data.get('json_uri') + 'cancel/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.get(cached_data.get('json_uri') + 'cancel/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.delete(cached_data.get('json_uri') + 'cancel/', format='json')
        self.assertHttpMethodNotAllowed(response)

    def test_08_mark_as_registered(self):
        # JSON
        infos = {"app": "invoicing", "resource": "InvoiceResource", "method": "mark_as_registered", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri') + 'mark_as_registered/', format='json')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)

        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['state'], "REGISTERED")
        self.assertEqual(deserialized['reference'][:7], expected_third_reference[:7])
        self.assertEqual(len(deserialized.get('history')), 4)
        self.assertEqual(deserialized.get('history')[0].get('resource_type'), 'changed_state_history_entry')
        self.assertEqual(deserialized.get('history')[0].get('state'), 'REGISTERED')

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri') + 'mark_as_registered/', format='xml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri') + 'mark_as_registered/', format='yaml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)

        # Check that other methods are not allowed
        response = self.api_client.post(cached_data.get('json_uri') + 'mark_as_registered/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.get(cached_data.get('json_uri') + 'mark_as_registered/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.delete(cached_data.get('json_uri') + 'mark_as_registered/', format='json')
        self.assertHttpMethodNotAllowed(response)

    def test_09_put_current_revision_is_not_hydrated_when_registered(self):
        invoice_data['current_revision']['line_items'][0]['quantity'] = decimal.Decimal("10")
        invoice_data['current_revision']['line_items'][0]['unit_price'] = decimal.Decimal("16.90")
        invoice_data['attachments'].append(self.cached_data.get('attachment_2_uri'))

        # JSON
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=invoice_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 2)
        self.assertEqual(deserialized['current_revision']['delivery_address']['city'], u'Grenoble')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'ITEM1')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'18.90')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'4.00')
        self.assertEqual(deserialized['amount'], u'90.42')
        self.assertEqual(len(deserialized.get('history')), 5)
        self.assertEqual(deserialized.get('history')[0].get('resource_type'), 'action_history_entry')
        self.assertEqual(deserialized.get('history')[0].get('action'), 'UPDATED')
        self.assertEqual(deserialized.get('history')[1].get('resource_type'), 'changed_state_history_entry')
        self.assertEqual(deserialized.get('history')[1].get('state'), 'REGISTERED')
        self.assertEqual(len(deserialized.get('attachments')), 2)
        self.assertIn(self.cached_data.get('attachment_1_uri'), deserialized.get('attachments'))
        self.assertIn(self.cached_data.get('attachment_2_uri'), deserialized.get('attachments'))

        response = self.api_client.get(deserialized['revisions'][-1], format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['line_items'][0]['quantity'], u'2.00')
        self.assertEqual(deserialized['line_items'][0]['unit_price'], u'19.90')

    def test_10_post_payments(self):
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['state'], u'REGISTERED')
        self.assertEqual(deserialized['amount'], u'90.42')
        self.assertEqual(deserialized['balance'], u'90.42')
        self.assertEqual(deserialized['paid'], u'0.00')
        self.assertEqual(len(deserialized['payments']), 0)

        # JSON
        infos = {"app": "invoicing", "resource": "PaymentResource", "method": "post_list", "serializer": "json"}
        payment_data_1.update(related_to=self.fullURItoAbsoluteURI(cached_data.get('json_uri')))
        response = self.api_client.post(self.resourceListURI('payment'), format='json', polymorph_to='invoice_payment', data=payment_data_1)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        payment_1_uri = self.fullURItoAbsoluteURI(response.get('location'))

        # Checks
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['state'], u'PART_PAID')
        self.assertEqual(deserialized['amount'], u'90.42')
        self.assertEqual(deserialized['balance'], u'80.00')
        self.assertEqual(deserialized['paid'], u'10.42')
        self.assertEqual(len(deserialized['payments']), 1)
        self.assertIn(payment_1_uri, deserialized['payments'])

        # Balance
        payment_data_2.update(related_to=self.fullURItoAbsoluteURI(cached_data.get('json_uri')))
        response = self.api_client.post(self.resourceListURI('payment'), format='json', polymorph_to='invoice_payment', data=payment_data_2)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        payment_2_uri = self.fullURItoAbsoluteURI(response.get('location'))

        # Checks
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['state'], u'PAID')
        self.assertEqual(deserialized['amount'], u'90.42')
        self.assertEqual(deserialized['balance'], u'0.00')
        self.assertEqual(deserialized['paid'], u'90.42')
        self.assertEqual(len(deserialized['payments']), 2)
        self.assertIn(payment_1_uri, deserialized['payments'])
        self.assertIn(payment_2_uri, deserialized['payments'])

        # XML
        infos.update(serializer='xml')
        payment_data_1.update(related_to=self.fullURItoAbsoluteURI(cached_data.get('xml_uri')))
        response = self.api_client.post(self.resourceListURI('payment'), format='xml', polymorph_to='invoice_payment', data=payment_data_1)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        payment_data_1.update(related_to=self.fullURItoAbsoluteURI(cached_data.get('yaml_uri')))
        response = self.api_client.post(self.resourceListURI('payment'), format='yaml', polymorph_to='invoice_payment', data=payment_data_1)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_11_delete_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "InvoiceResource", "method": "delete_detail", "serializer": "json"}
        response = self.api_client.delete(cached_data.get('json_uri'), format='json')
        self.assertHttpBadRequest(response)  # Not in a deletable state (registered)
        response = self.api_client.delete(cached_data.get('json_uri2'), format='json')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('json_uri2'), format='json')
        self.assertHttpNotFound(response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.delete(cached_data.get('xml_uri'), format='xml')
        self.assertHttpBadRequest(response)  # Not in a deletable state (registered)
        response = self.api_client.delete(cached_data.get('xml_uri2'), format='xml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('xml_uri2'), format='xml')
        self.assertHttpNotFound(response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.delete(cached_data.get('yaml_uri'), format='yaml')
        self.assertHttpBadRequest(response)  # Not in a deletable state (registered)
        response = self.api_client.delete(cached_data.get('yaml_uri2'), format='yaml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('yaml_uri2'), format='yaml')
        self.assertHttpNotFound(response)

    def test_12_cancel(self):
        # JSON
        infos = {"app": "invoicing", "resource": "InvoiceResource", "method": "cancel", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri') + 'cancel/', format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # Checks credit note and invoice
        deserialized = self.deserialize(response)
        response = self.api_client.get(deserialized.get('credit_note_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized_credit_note = self.deserialize(response)
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized_invoice = self.deserialize(response)
        self.assertEqual(deserialized_invoice.get('state'), u'CANCELLED')
        self.assertEqual(
            decimal.Decimal(deserialized_invoice.get('amount')) +
            decimal.Decimal(deserialized_credit_note.get('amount')),
            decimal.Decimal("0")
        )
        self.assertEqual(len(deserialized_invoice.get('history')), 6)
        self.assertEqual(deserialized_invoice.get('history')[0].get('resource_type'), 'changed_state_history_entry')
        self.assertEqual(deserialized_invoice.get('history')[0].get('state'), 'CANCELLED')

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri') + 'cancel/', format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri') + 'cancel/', format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

        # Check that other methods are not allowed
        response = self.api_client.post(cached_data.get('json_uri') + 'cancel/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.get(cached_data.get('json_uri') + 'cancel/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.delete(cached_data.get('json_uri') + 'cancel/', format='json')
        self.assertHttpMethodNotAllowed(response)

    def test_13_delete_list(self):
        # JSON
        response = self.api_client.delete(self.resourceListURI('invoice'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('invoice'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('invoice'), format='yaml')
        self.assertHttpMethodNotAllowed(response)


class DownPaymentInvoiceResourceTest(InvoiceBaseResourceTest):
    @classmethod
    def setUpClass(cls):
        from contacts.models import Organization
        from invoicing.models import Quotation, Item, InvoiceItem, Currency
        super(DownPaymentInvoiceResourceTest, cls).setUpClass()

        # Create an organization which will be referenced
        organization = Organization.objects.create(tenant=settings.TENANT, creator=settings.VOSAE_USER, corporate_name="My Company", private=False)

        item = Item.objects(unit_price=19.9).first()
        line_item = InvoiceItem(
            reference=item.reference,
            description=item.description,
            quantity=decimal.Decimal('2'),
            unit_price=item.unit_price,
            tax=item.tax,
            item_id=item.id
        )
        quotation = Quotation(tenant=settings.TENANT, issuer=settings.VOSAE_USER, account_type='RECEIVABLE')
        quotation.current_revision.currency = Currency.objects.get(symbol='EUR').get_snapshot()
        quotation.current_revision.line_items.append(line_item)
        quotation.current_revision.organization = organization
        quotation.save()
        down_payment_invoice_1 = quotation.make_down_payment_invoice(
            issuer=settings.VOSAE_USER,
            percentage=decimal.Decimal('0.3'),
            tax=item.tax,
            date=datetime.date.today()
        )
        down_payment_invoice_2 = quotation.make_down_payment_invoice(
            issuer=settings.VOSAE_USER,
            percentage=decimal.Decimal('0.3'),
            tax=item.tax,
            date=datetime.date.today()
        )
        down_payment_invoice_3 = quotation.make_down_payment_invoice(
            issuer=settings.VOSAE_USER,
            percentage=decimal.Decimal('0.3'),
            tax=item.tax,
            date=datetime.date.today()
        )
        cls.cached_data = {
            'json_uri': cls.resourceDetailURI('down_payment_invoice', unicode(down_payment_invoice_1.id)),
            'xml_uri': cls.resourceDetailURI('down_payment_invoice', unicode(down_payment_invoice_2.id)),
            'yaml_uri': cls.resourceDetailURI('down_payment_invoice', unicode(down_payment_invoice_3.id)),
        }
        cls.created_documents += [organization]

    def test_01_post_list(self):
        # JSON
        response = self.api_client.post(self.resourceListURI('down_payment_invoice'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.post(self.resourceListURI('down_payment_invoice'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.post(self.resourceListURI('down_payment_invoice'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_02_get_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "DownPaymentInvoiceResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('down_payment_invoice'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('down_payment_invoice'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('down_payment_invoice'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "DownPaymentInvoiceResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(self.cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 0)
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'DOWN-PAYMENT')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['description'], u'30%% down-payment on quotation %s' % expected_second_reference)
        self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'11.94')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'1.00')
        self.assertEqual(deserialized['amount'], u'14.28')
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.cached_data.get('xml_uri'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.cached_data.get('yaml_uri'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_04_put_list(self):
        # JSON
        response = self.api_client.put(self.resourceListURI('down_payment_invoice'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('down_payment_invoice'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('down_payment_invoice'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        # JSON
        response = self.api_client.put(self.cached_data.get('json_uri'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.cached_data.get('xml_uri'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.cached_data.get('yaml_uri'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_06_cancel(self):
        # JSON
        infos = {"app": "invoicing", "resource": "DownPaymentInvoiceResource", "method": "cancel", "serializer": "json"}
        response = self.api_client.put(self.cached_data.get('json_uri') + 'cancel/', format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # Checks credit note and down payment invoice
        deserialized = self.deserialize(response)
        response = self.api_client.get(deserialized.get('credit_note_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized_credit_note = self.deserialize(response)
        response = self.api_client.get(self.cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized_invoice = self.deserialize(response)
        self.assertEqual(deserialized_invoice.get('state'), u'CANCELLED')
        self.assertEqual(
            decimal.Decimal(deserialized_invoice.get('amount')) +
            decimal.Decimal(deserialized_credit_note.get('amount')),
            decimal.Decimal("0")
        )

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(self.cached_data.get('xml_uri') + 'cancel/', format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(self.cached_data.get('yaml_uri') + 'cancel/', format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

        # Check that other methods are not allowed
        response = self.api_client.post(self.cached_data.get('json_uri') + 'cancel/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.get(self.cached_data.get('json_uri') + 'cancel/', format='json')
        self.assertHttpMethodNotAllowed(response)

        response = self.api_client.delete(self.cached_data.get('json_uri') + 'cancel/', format='json')
        self.assertHttpMethodNotAllowed(response)

    def test_07_delete_detail(self):
        # JSON
        response = self.api_client.delete(self.cached_data.get('json_uri'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.cached_data.get('xml_uri'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.cached_data.get('yaml_uri'), format='yaml')
        self.assertHttpMethodNotAllowed(response)

    def test_08_delete_list(self):
        # JSON
        response = self.api_client.delete(self.resourceListURI('down_payment_invoice'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('down_payment_invoice'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('down_payment_invoice'), format='yaml')
        self.assertHttpMethodNotAllowed(response)


class CreditNoteResourceTest(InvoiceBaseResourceTest):
    @classmethod
    def setUpClass(cls):
        from contacts.models import Organization
        from invoicing.models import Quotation, Item, InvoiceItem, Currency
        super(CreditNoteResourceTest, cls).setUpClass()

        # Create an organization which will be referenced
        organization = Organization(tenant=settings.TENANT, creator=settings.VOSAE_USER, corporate_name="My Company", private=False).save()

        item = Item.objects.first()
        line_item = InvoiceItem(
            reference=item.reference,
            description=item.description,
            quantity=decimal.Decimal('2'),
            unit_price=item.unit_price,
            tax=item.tax,
            item_id=item.id
        )
        quotation = Quotation(tenant=settings.TENANT, issuer=settings.VOSAE_USER, account_type='RECEIVABLE')
        quotation.current_revision.currency = Currency.objects.get(symbol='EUR').get_snapshot()
        quotation.current_revision.line_items.append(line_item)
        quotation.current_revision.organization = organization
        quotation.save()
        down_payment_invoice_1 = quotation.make_down_payment_invoice(
            issuer=settings.VOSAE_USER,
            percentage=decimal.Decimal('0.3'),
            tax=item.tax,
            date=datetime.date.today()
        )
        credit_note_1 = down_payment_invoice_1.cancel(settings.VOSAE_USER)
        down_payment_invoice_2 = quotation.make_down_payment_invoice(
            issuer=settings.VOSAE_USER,
            percentage=decimal.Decimal('0.3'),
            tax=item.tax,
            date=datetime.date.today()
        )
        credit_note_2 = down_payment_invoice_2.cancel(settings.VOSAE_USER)
        down_payment_invoice_3 = quotation.make_down_payment_invoice(
            issuer=settings.VOSAE_USER,
            percentage=decimal.Decimal('0.3'),
            tax=item.tax,
            date=datetime.date.today()
        )
        credit_note_3 = down_payment_invoice_3.cancel(settings.VOSAE_USER)
        cls.cached_data = {
            'json_uri': cls.resourceDetailURI('credit_note', unicode(credit_note_1.id)),
            'xml_uri': cls.resourceDetailURI('credit_note', unicode(credit_note_2.id)),
            'yaml_uri': cls.resourceDetailURI('credit_note', unicode(credit_note_3.id)),
        }
        cls.created_documents += [organization]

    def test_01_post_list(self):
        # JSON
        response = self.api_client.post(self.resourceListURI('credit_note'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.post(self.resourceListURI('credit_note'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.post(self.resourceListURI('credit_note'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_02_get_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "CreditNoteResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('credit_note'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('credit_note'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('credit_note'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "CreditNoteResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(self.cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized['current_revision']['line_items']), 1)
        self.assertEqual(len(deserialized['revisions']), 0)
        self.assertEqual(deserialized['current_revision']['line_items'][0]['reference'], u'DOWN-PAYMENT')
        self.assertEqual(deserialized['current_revision']['line_items'][0]['description'], u'30%% down-payment on quotation %s' % expected_first_reference)
        # self.assertEqual(deserialized['current_revision']['line_items'][0]['unit_price'], u'11.94')  # XXX Should be fixed
        self.assertEqual(deserialized['current_revision']['line_items'][0]['quantity'], u'1.00')
        # self.assertEqual(deserialized['amount'], u'14.28')  # XXX Should be fixed
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.cached_data.get('xml_uri'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.cached_data.get('yaml_uri'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_04_put_list(self):
        # JSON
        response = self.api_client.put(self.resourceListURI('credit_note'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('credit_note'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('credit_note'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        # JSON
        response = self.api_client.put(self.cached_data.get('json_uri'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.cached_data.get('xml_uri'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.cached_data.get('yaml_uri'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_06_delete_detail(self):
        # JSON
        response = self.api_client.delete(self.cached_data.get('json_uri'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.cached_data.get('xml_uri'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.cached_data.get('yaml_uri'), format='yaml')
        self.assertHttpMethodNotAllowed(response)

    def test_07_delete_list(self):
        # JSON
        response = self.api_client.delete(self.resourceListURI('credit_note'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('credit_note'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('credit_note'), format='yaml')
        self.assertHttpMethodNotAllowed(response)
