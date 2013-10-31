# -*- coding:Utf-8 -*-

from django.conf import settings

from vosae_utils import VosaeApiTest


organization_data = {
    "corporate_name": u"Company A",
    "addresses": [
        {
            "city": u"Grenoble",
            "country": u"FRANCE",
            "postal_code": u"38000",
            "street_address": u"1 Rue de Grenoble",
            "type": u"WORK"
        }
    ],
    "emails": [
        {
            "email": u"contact@naeka.fr",
            "type": u"WORK"
        }
    ],
    "phones": [
        {
            "phone": u"04 05 06 07 08",
            "type": u"WORK"
        }
    ]
}

contact_data = {
    "firstname": u"Employee",
    "name": u"A",
    "photo_source": u"GRAVATAR",
    "gravatar_mail": u"api-employee@naeka.fr",
    "addresses": [
        {
            "city": u"Grenoble",
            "country": u"FRANCE",
            "postal_code": u"38000",
            "street_address": u"1 Rue de Grenoble",
            "type": u"WORK"
        }
    ],
    "emails": [
        {
            "email": u"api-employee@naeka.fr",
            "type": u"HOME"
        }
    ],
    "phones": [
        {
            "phone": u"06 01 02 03 04",
            "subtype": u"CELL",
            "type": u"WORK"
        },
        {
            "phone": u"04 05 06 07 08",
            "type": u"WORK"
        }
    ],
    "note": u"Phones are not real!",
}


cached_data = {}


class OrganizationResourceTest(VosaeApiTest):

    def test_01_post_list(self):
        # JSON
        infos = {"app": "contacts", "resource": "OrganizationResource", "method": "post_list", "serializer": "json"}
        response = self.api_client.post(self.resourceListURI('organization'), format='json', data=organization_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.post(self.resourceListURI('organization'), format='xml', data=organization_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.post(self.resourceListURI('organization'), format='yaml', data=organization_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {"app": "contacts", "resource": "OrganizationResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('organization'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('organization'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('organization'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "contacts", "resource": "OrganizationResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(self.deserialize(response).get('corporate_name'), u'Company A')
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
        response = self.api_client.put(self.resourceListURI('organization'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('organization'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('organization'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        organization_data.update(corporate_name=u"Company B")
        # JSON
        infos = {"app": "contacts", "resource": "OrganizationResource", "method": "put_detail", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=organization_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(self.deserialize(response).get('corporate_name'), u'Company B')

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=organization_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=organization_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_delete_detail(self):
        # JSON
        infos = {"app": "contacts", "resource": "OrganizationResource", "method": "delete_detail", "serializer": "json"}
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
        response = self.api_client.delete(self.resourceListURI('organization'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('organization'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('organization'), format='yaml')
        self.assertHttpMethodNotAllowed(response)

    def test_08_repost_inactive(self):
        # JSON
        # No uniqueness constraint with organizations, repost should be accepted
        response = self.api_client.post(self.resourceListURI('organization'), format='json', data=organization_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        cached_data.update(json_uri2=response.get('location'))

    def test_09_get_list_with_inactive(self):
        # JSON
        response = self.api_client.get(self.resourceListURI('organization'), format='json')
        self.assertValidJSONResponse(response)
        deserialized_objects = self.deserialize(response).get('objects')
        uri_list = [organization.get('resource_uri') for organization in deserialized_objects]
        self.assertEqual(len(deserialized_objects), 1)
        self.assertNotIn(self.fullURItoAbsoluteURI(cached_data.get('json_uri')), uri_list)
        self.assertIn(self.fullURItoAbsoluteURI(cached_data.get('json_uri2')), uri_list)


class ContactResourceTest(VosaeApiTest):

    @classmethod
    def setUpClass(cls):
        from contacts.models import Organization
        super(ContactResourceTest, cls).setUpClass()
        # Create first an organization which will be referenced
        organization = Organization(tenant=settings.TENANT, creator=settings.VOSAE_USER, corporate_name=u"My Company", private=False)
        organization.save()
        contact_data.update(organization=cls.resourceDetailURI('organization', unicode(organization.id)))
        cls.created_documents = [organization]

    @classmethod
    def tearDownClass(cls):
        for document in cls.created_documents:
            document.delete(force=True)
        super(ContactResourceTest, cls).tearDownClass()

    def test_01_post_list(self):
        # JSON
        infos = {"app": "contacts", "resource": "ContactResource", "method": "post_list", "serializer": "json"}
        response = self.api_client.post(self.resourceListURI('contact'), format='json', data=contact_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.post(self.resourceListURI('contact'), format='xml', data=contact_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.post(self.resourceListURI('contact'), format='yaml', data=contact_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {"app": "contacts", "resource": "ContactResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('contact'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('contact'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('contact'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "contacts", "resource": "ContactResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized.get('firstname'), u'Employee')
        self.assertEqual(deserialized.get('name'), u'A')
        self.assertEqual(deserialized.get('addresses')[0]['city'], u'Grenoble')
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
        response = self.api_client.put(self.resourceListURI('contact'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('contact'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('contact'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        contact_data.update(firstname=u"Chief", name=u"B")
        # JSON
        infos = {"app": "contacts", "resource": "ContactResource", "method": "put_detail", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=contact_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized.get('firstname'), u'Chief')
        self.assertEqual(deserialized.get('name'), u'B')

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=contact_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=contact_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_delete_detail(self):
        # JSON
        infos = {"app": "contacts", "resource": "ContactResource", "method": "delete_detail", "serializer": "json"}
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
        response = self.api_client.delete(self.resourceListURI('contact'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('contact'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('contact'), format='yaml')
        self.assertHttpMethodNotAllowed(response)

    def test_08_repost_inactive(self):
        # JSON
        # No uniqueness constraint with contacts, repost should be accepted
        response = self.api_client.post(self.resourceListURI('contact'), format='json', data=contact_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        cached_data.update(json_uri2=response.get('location'))

    def test_09_get_list_with_inactive(self):
        # JSON
        response = self.api_client.get(self.resourceListURI('contact'), format='json')
        self.assertValidJSONResponse(response)
        deserialized_objects = self.deserialize(response).get('objects')
        uri_list = [contact.get('resource_uri') for contact in deserialized_objects]
        self.assertEqual(len(deserialized_objects), 1)
        self.assertNotIn(self.fullURItoAbsoluteURI(cached_data.get('json_uri')), uri_list)
        self.assertIn(self.fullURItoAbsoluteURI(cached_data.get('json_uri2')), uri_list)
