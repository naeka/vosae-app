# -*- coding:Utf-8 -*-

from django.conf import settings
from django.core.files.base import ContentFile

from vosae_utils import VosaeApiTest

tenant_data = {
    u"name": u"My Company",
    u"email": u"contact@naeka.fr",
    u"phone": u"0102030405",
    u"fax": u"0102030400",
    u"billing_address": {
        u"city": u"Paris",
        u"country": u"France",
        u"postal_code": u"75001",
        u"street_address": u"This address is a fake",
    },
    u"postal_address": {
        u"city": u"Grenoble",
        u"country": u"France",
        u"postal_code": u"75001",
        u"street_address": u"This address is a fake",
    },
    u"registration_info": {
        u"business_entity": u"Inc.",
        u"resource_type": u"us_registration_info",
        u"share_capital": u"200,000 USD"
    },
    u"report_settings": {}
}

file_data = {
    'uploaded_file': ContentFile('Test file A', name='test file.txt')
}

vosae_group_data = {
    u"name": u"My new group",
    u"permissions": [
        u"core_access", u"contacts_access", u"invoicing_access", u"organizer_access", u"see_invoicebase",
        u"add_invoicebase", u"change_invoicebase", u"delete_invoicebase", u"see_item", u"add_item",
        u"change_item", u"delete_item", u"see_vosaefile", u"add_vosaefile", u"delete_vosaefile",
        u"see_contact", u"add_contact", u"change_contact", u"delete_contact"
    ]
}

vosae_user_data = {
    "email": "nobody@vosae.com",
    "settings": {},
    "specific_permissions": {
        "invoicing_access": False
    }
}

cached_data = {}


class TenantResourceTest(VosaeApiTest):

    def _fixture_teardown(self):
        # Vosae tenants group association should persist among all tests
        pass

    @classmethod
    def setUpClass(cls):
        from invoicing.models import Currency
        super(TenantResourceTest, cls).setUpClass()
        # Retrieve currency which will be referenced
        eur = Currency.objects.get(symbol='EUR')

        tenant_data.update(
            supported_currencies=[cls.resourceDetailURI('currency', unicode(eur.id))],
            default_currency=cls.resourceDetailURI('currency', unicode(eur.id))
        )

    def test_01_post_list(self):
        # JSON
        infos = {"app": "core", "resource": "TenantResource", "method": "post_list", "serializer": "json"}
        response = self.api_client.post(self.resourceListURI('tenant'), format='json', data=tenant_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.post(self.resourceListURI('tenant'), format='xml', data=tenant_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.post(self.resourceListURI('tenant'), format='yaml', data=tenant_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "TenantResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('tenant'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)
        deserialized = self.deserialize(response)

        # SQL database is rollback after every test, so user losts access to tenants created in test_01_post_list
        self.assertEqual(len(deserialized.get('objects')), 4)
        self.assertEqual(deserialized.get('meta').get('total_count'), 4)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('tenant'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('tenant'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "TenantResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized.get('name'), u'My Company')
        self.assertEqual(deserialized.get('slug'), u'my-company')
        self.assertEqual(deserialized.get('report_settings').get('font_size'), 10)
        self.assertEqual(deserialized.get('report_settings').get('font_name'), u'Bariol')
        self.assertEqual(deserialized.get('report_settings').get('language'), u'en')

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
        response = self.api_client.put(self.resourceListURI('tenant'), format='json', data={}, HTTP_X_TENANT=settings.TENANT.slug)
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('tenant'), format='xml', data={}, HTTP_X_TENANT=settings.TENANT.slug)
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('tenant'), format='yaml', data={}, HTTP_X_TENANT=settings.TENANT.slug)
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "TenantResource", "method": "put_detail", "serializer": "json"}
        tenant_data['report_settings'].update(font_name=u"Arial", font_size=11)
        tenant_data.update(slug="immutable")
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=tenant_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized.get('name'), u'My Company')
        self.assertEqual(deserialized.get('slug'), u'my-company')
        self.assertEqual(deserialized.get('report_settings').get('font_size'), 11)
        self.assertEqual(deserialized.get('report_settings').get('font_name'), u'Arial')

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=tenant_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=tenant_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_delete_detail(self):
        # JSON
        response = self.api_client.delete(cached_data.get('json_uri'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(cached_data.get('xml_uri'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(cached_data.get('yaml_uri'), format='yaml')
        self.assertHttpMethodNotAllowed(response)

    def test_07_delete_list(self):
        # JSON
        response = self.api_client.delete(self.resourceListURI('tenant'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('tenant'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('tenant'), format='yaml')
        self.assertHttpMethodNotAllowed(response)


class VosaeFileResourceTest(VosaeApiTest):

    def test_01_post_list(self):
        # JSON
        infos = {"app": "core", "resource": "VosaeFileResource", "method": "post_list", "serializer": "json"}
        response = self.api_client.post(self.resourceListURI('file'), format='json', data=file_data, disposition='form-data')
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))

        # XML
        infos.update(serializer='xml')
        file_data.update(uploaded_file=ContentFile('Test file B', name='test file.txt'))
        response = self.api_client.post(self.resourceListURI('file'), format='xml', data=file_data, disposition='form-data')
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        file_data.update(uploaded_file=ContentFile('Test file C', name='test file.txt'))
        response = self.api_client.post(self.resourceListURI('file'), format='yaml', data=file_data, disposition='form-data')
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))

    def test_02_get_list(self):
        # JSON
        response = self.api_client.get(self.resourceListURI('file'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.get(self.resourceListURI('file'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.get(self.resourceListURI('file'), format='yaml')
        self.assertHttpMethodNotAllowed(response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "core", "resource": "VosaeFileResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(self.deserialize(response).get('name'), u'test file.txt')
        self.assertEqual(self.deserialize(response).get('size'), 11)
        self.assertKeys(self.deserialize(response), [u'created_at', u'modified_at', u'id', u'ttl', u'issuer', u'name', u'size', u'sha1_checksum', u'download_link', u'stream_link', u'resource_uri'])
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
        response = self.api_client.put(self.resourceListURI('file'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('file'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('file'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        # JSON
        infos = {"app": "core", "resource": "VosaeFileResource", "method": "put_detail", "serializer": "json"}
        file_data.update(uploaded_file=ContentFile('File 1', name='file put.txt'))
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=file_data, disposition='form-data')
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized.get('name'), u'file put.txt')
        self.assertEqual(deserialized.get('size'), 6)

        # XML
        infos.update(serializer='xml')
        file_data.update(uploaded_file=ContentFile('Test file 2', name='file put.txt'))
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=file_data, disposition='form-data')
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        file_data.update(uploaded_file=ContentFile('Test file 3', name='file put.txt'))
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=file_data, disposition='form-data')
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_delete_detail(self):
        # JSON
        infos = {"app": "core", "resource": "VosaeFileResource", "method": "delete_detail", "serializer": "json"}
        response = self.api_client.delete(cached_data.get('json_uri'), format='json')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertHttpNotFound(response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.delete(cached_data.get('xml_uri'), format='xml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('xml_uri'), format='xml')
        self.assertHttpNotFound(response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.delete(cached_data.get('yaml_uri'), format='yaml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('yaml_uri'), format='yaml')
        self.assertHttpNotFound(response)

    def test_07_delete_list(self):
        # JSON
        response = self.api_client.delete(self.resourceListURI('file'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('file'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('file'), format='yaml')
        self.assertHttpMethodNotAllowed(response)


class VosaeGroupResourceTest(VosaeApiTest):

    def test_01_post_list(self):
        # JSON
        infos = {"app": "core", "resource": "VosaeGroupResource", "method": "post_list", "serializer": "json"}
        response = self.api_client.post(self.resourceListURI('group'), format='json', data=vosae_group_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))

        # XML
        infos.update(serializer='xml')
        vosae_group_data.update(name=u"My new group 2")
        response = self.api_client.post(self.resourceListURI('group'), format='xml', data=vosae_group_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        vosae_group_data.update(name=u"My new group 3")
        response = self.api_client.post(self.resourceListURI('group'), format='yaml', data=vosae_group_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "VosaeGroupResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('group'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized.get('objects')), 4)  # Administrator + these three
        self.assertEqual(deserialized.get('meta').get('total_count'), 4)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('group'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('group'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "VosaeGroupResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized.get('name'), u'My new group')

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
        response = self.api_client.put(self.resourceListURI('group'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('group'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('group'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "VosaeGroupResource", "method": "put_detail", "serializer": "json"}
        vosae_group_data.update(name=u"An updated name")
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=vosae_group_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized.get('name'), u'An updated name')

        # XML
        infos.update(serializer='xml')
        vosae_group_data.update(name=u"An updated name 2")
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=vosae_group_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        vosae_group_data.update(name=u"An updated name 3")
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=vosae_group_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_delete_detail(self):
        # JSON
        infos = {"app": "organizer", "resource": "VosaeGroupResource", "method": "delete_detail", "serializer": "json"}
        response = self.api_client.delete(cached_data.get('json_uri'), format='json')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertHttpNotFound(response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.delete(cached_data.get('xml_uri'), format='xml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('xml_uri'), format='xml')
        self.assertHttpNotFound(response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.delete(cached_data.get('yaml_uri'), format='yaml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('yaml_uri'), format='yaml')
        self.assertHttpNotFound(response)

    def test_07_delete_list(self):
        # JSON
        response = self.api_client.delete(self.resourceListURI('group'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('group'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('group'), format='yaml')
        self.assertHttpMethodNotAllowed(response)


class VosaeUserResourceTest(VosaeApiTest):

    def _fixture_teardown(self):
        # Django users should persist among all tests
        pass

    @classmethod
    def setUpClass(cls):
        from core.models import VosaeGroup
        super(VosaeUserResourceTest, cls).setUpClass()
        # Retrieve group which will be referenced
        group = VosaeGroup.objects.filter(tenant=settings.TENANT).first()

        vosae_user_data.update(groups=[cls.resourceDetailURI('group', unicode(group.id))])

    def test_01_post_list(self):
        # JSON
        infos = {"app": "core", "resource": "VosaeUserResource", "method": "post_list", "serializer": "json"}
        response = self.api_client.post(self.resourceListURI('user'), format='json', data=vosae_user_data)
        # Default user has this email, HTTP 409 expected
        self.assertHttpConflict(response)
        self.assertEqual(response.content, u"A document with this email already exists. It can be waked up thanks to the X-WakeUp header (if in a DELETED/INACTIVE status)  or you can set different values")
        vosae_user_data.update(email=u"nobody1@vosae.com")
        response = self.api_client.post(self.resourceListURI('user'), format='json', data=vosae_user_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))

        # XML
        infos.update(serializer='xml')
        vosae_user_data.update(email=u"nobody2@vosae.com")
        response = self.api_client.post(self.resourceListURI('user'), format='xml', data=vosae_user_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        vosae_user_data.update(email=u"nobody3@vosae.com")
        response = self.api_client.post(self.resourceListURI('user'), format='yaml', data=vosae_user_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {"app": "invoicing", "resource": "VosaeUserResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('user'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized.get('objects')), 4)  # Default user + these three
        self.assertEqual(deserialized.get('meta').get('total_count'), 4)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('user'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('user'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "VosaeUserResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)
        deserialized = self.deserialize(response)
        self.assertIn(u'core_access', deserialized.get('permissions'))
        self.assertNotIn(u'invoicing_access', deserialized.get('permissions'))
        self.assertEqual(deserialized.get('status'), u'ACTIVE')
        self.assertEqual(deserialized.get('settings').get('language_code'), None)

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
        response = self.api_client.put(self.resourceListURI('user'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('user'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('user'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "VosaeUserResource", "method": "put_detail", "serializer": "json"}
        vosae_user_data['settings'].update(email_signature=u'An email signature')
        vosae_user_data.update(
            email=u'E-mail can\'t be changed and is treated as readonly after POST',
            specific_permissions={}
        )
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=vosae_user_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized.get('email'), u'nobody1@vosae.com')  # Checks that it is immutable
        self.assertIn(u'core_access', deserialized.get('permissions'))
        self.assertIn(u'invoicing_access', deserialized.get('permissions'))
        self.assertEqual(deserialized.get('status'), u'ACTIVE')
        self.assertEqual(deserialized.get('settings').get('email_signature'), u'An email signature')

        # XML
        infos.update(serializer='xml')
        vosae_user_data.update(name=u"An updated name 2")
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=vosae_user_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        vosae_user_data.update(name=u"An updated name 3")
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=vosae_user_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_delete_detail(self):
        # JSON
        infos = {"app": "invoicing", "resource": "VosaeUserResource", "method": "delete_detail", "serializer": "json"}
        response = self.api_client.delete(cached_data.get('json_uri'), format='json')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertIn('status', deserialized)
        self.assertEqual('DELETED', deserialized.get('status'))

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
        response = self.api_client.delete(self.resourceListURI('user'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('user'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('user'), format='yaml')
        self.assertHttpMethodNotAllowed(response)

    def test_08_repost_inactive(self):
        # JSON
        vosae_user_data.update(email=u'nobody1@vosae.com')
        response = self.api_client.post(self.resourceListURI('user'), format='json', data=vosae_user_data)
        self.assertHttpConflict(response)
        self.assertEqual(response.content, 'A document with this email already exists. It can be waked up thanks to the X-WakeUp header (if in a DELETED/INACTIVE status)  or you can set different values')

        response = self.api_client.post(self.resourceListURI('user'), format='json', data=vosae_user_data, HTTP_X_WAKEUP='ACTIVE')
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)


class VosaeSearchResourceTest(VosaeApiTest):

    def test_01_get_list(self):
        # JSON
        infos = {"app": "core", "resource": "VosaeSearchResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('search') + '?q=nobo', format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('search') + '?q=nobo', format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('search') + '?q=nobo', format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_02_other_method_not_allowed(self):
        # JSON
        response = self.api_client.post(self.resourceListURI('search'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)
        response = self.api_client.put(self.resourceListURI('search'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)
        response = self.api_client.delete(self.resourceListURI('search'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.post(self.resourceListURI('search'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)
        response = self.api_client.put(self.resourceListURI('search'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)
        response = self.api_client.delete(self.resourceListURI('search'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.post(self.resourceListURI('search'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)
        response = self.api_client.put(self.resourceListURI('search'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)
        response = self.api_client.delete(self.resourceListURI('search'), format='yaml')
        self.assertHttpMethodNotAllowed(response)


class VosaeCorsMiddlewareProcessResponseTest(VosaeApiTest):

    def test_01_no_cors_header_on_same_domain(self):
        response = self.api_client.get('/api/v1/', format='json')
        self.assertTrue(response.has_header('X-Frame-Options'))
        self.assertFalse(response.has_header('Access-Control-Allow-Origin'))
        self.assertFalse(response.has_header('Access-Control-Expose-Headers'))

    def test_02_no_cors_header_on_non_api_endpoints(self):
        response = self.api_client.get('/en/account/signup/', format='json')
        self.assertTrue(response.has_header('X-Frame-Options'))
        self.assertFalse(response.has_header('Access-Control-Allow-Origin'))
        self.assertFalse(response.has_header('Access-Control-Expose-Headers'))

    def test_03_cors_header_on_api_endpoints(self):
        response = self.api_client.get('/api/v1/', format='json', HTTP_ORIGIN='https://localhost:8001')
        self.assertTrue(response.has_header('X-Frame-Options'))
        self.assertTrue(response.has_header('Access-Control-Allow-Credentials'))
        self.assertTrue(response.has_header('Access-Control-Allow-Origin'))
        self.assertTrue(response.has_header('Access-Control-Expose-Headers'))
        self.assertEqual(response['Access-Control-Allow-Credentials'], 'true')
        self.assertEqual(response['Access-Control-Allow-Origin'], 'https://localhost:8001')
        self.assertEqual(response['Access-Control-Expose-Headers'], 'x-tenant, x-report-language, x-wakeup')
