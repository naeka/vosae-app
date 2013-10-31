# -*- coding:Utf-8 -*-

from vosae_utils import VosaeApiTest


api_key_data = {
    'label': u'Api key for application A',
}

cached_data = {}


class ApiKeyResourceTest(VosaeApiTest):

    def _fixture_teardown(self):
        # Api keys should persist among all tests
        pass

    def test_01_post_list(self):
        # JSON
        infos = {'app': 'account', 'resource': 'ApiKeyResource', 'method': 'post_list', 'serializer': 'json'}
        response = self.api_client.post(self.resourceListURI('api_key'), format='json', data=api_key_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.assertKeys(self.deserialize(response), [u'id', u'label', u'created_at', u'key', u'resource_uri'])
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))
        response = self.api_client.post(self.resourceListURI('api_key'), format='json', data=api_key_data)
        self.assertHttpBadRequest(response)  # Api key label must be unique

        # XML
        infos.update(serializer='xml')
        api_key_data.update(label=api_key_data.get('label')[:-1] + 'B')
        response = self.api_client.post(self.resourceListURI('api_key'), format='xml', data=api_key_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        api_key_data.update(label=api_key_data.get('label')[:-1] + 'C')
        response = self.api_client.post(self.resourceListURI('api_key'), format='yaml', data=api_key_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {'app': 'account', 'resource': 'ApiKeyResource', 'method': 'get_list', 'serializer': 'json'}
        response = self.api_client.get(self.resourceListURI('api_key'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('api_key'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('api_key'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {'app': 'account', 'resource': 'ApiKeyResource', 'method': 'get_detail', 'serializer': 'json'}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(self.deserialize(response)['label'], u'Api key for application A')
        self.assertKeys(self.deserialize(response), [u'id', u'label', u'created_at', u'resource_uri'])
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
        response = self.api_client.put(self.resourceListURI('api_key'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('api_key'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('api_key'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        # JSON
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_06_delete_detail(self):
        # JSON
        infos = {'app': 'account', 'resource': 'ApiKeyResource', 'method': 'delete_detail', 'serializer': 'json'}
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
        infos = {'app': 'account', 'resource': 'ApiKeyResource', 'method': 'delete_list', 'serializer': 'json'}
        response = self.api_client.delete(self.resourceListURI('api_key'), format='json')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.delete(self.resourceListURI('api_key'), format='xml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.delete(self.resourceListURI('api_key'), format='yaml')
        self.assertHttpAccepted(response)
        self.save_test_result(infos, response)
