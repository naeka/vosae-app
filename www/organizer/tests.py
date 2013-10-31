# -*- coding:Utf-8 -*-

from django.conf import settings

from vosae_utils import VosaeApiTest


vosae_calendar_data = {
    'summary': u'My Calendar',
    'timezone': u'Europe/Paris',
    'acl': {
        'rules': [
            {
                'role': u'OWNER'
            }
        ]
    }
}

vosae_event_data = {
    'summary': u'My event',
    'start': {
        'date': u'2013-01-01',
    },
    'end': {
        'date': u'2013-01-01',
    }
}


cached_data = {}


class VosaeCalendarResourceTest(VosaeApiTest):

    def test_01_post_list(self):
        vosae_calendar_data['acl']['rules'][0].update(principal=self.resourceDetailURI('user', unicode(settings.VOSAE_USER.id)))
        # JSON
        infos = {"app": "organizer", "resource": "VosaeCalendarResource", "method": "post_list", "serializer": "json"}
        response = self.api_client.post(self.resourceListURI('vosae_calendar'), format='json', data=vosae_calendar_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.post(self.resourceListURI('vosae_calendar'), format='xml', data=vosae_calendar_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.post(self.resourceListURI('vosae_calendar'), format='yaml', data=vosae_calendar_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {"app": "organizer", "resource": "VosaeCalendarResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('vosae_calendar'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('vosae_calendar'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('vosae_calendar'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "organizer", "resource": "VosaeCalendarResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['summary'], u'My Calendar')
        self.assertEqual(deserialized['description'], None)
        self.assertEqual(deserialized['acl']['rules'][0]['role'], 'OWNER')
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
        response = self.api_client.put(self.resourceListURI('vosae_calendar'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('vosae_calendar'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('vosae_calendar'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        vosae_calendar_data['description'] = u'A small description'
        vosae_calendar_data['location'] = u'Paris, France'
        # JSON
        infos = {"app": "organizer", "resource": "VosaeCalendarResource", "method": "put_detail", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=vosae_calendar_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['summary'], u'My Calendar')
        self.assertEqual(deserialized['description'], u'A small description')
        self.assertEqual(deserialized['location'], u'Paris, France')

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=vosae_calendar_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=vosae_calendar_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_delete_detail(self):
        # JSON
        infos = {"app": "organizer", "resource": "VosaeCalendarResource", "method": "delete_detail", "serializer": "json"}
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
        response = self.api_client.delete(self.resourceListURI('vosae_calendar'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('vosae_calendar'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('vosae_calendar'), format='yaml')
        self.assertHttpMethodNotAllowed(response)


class CalendarListResourceTest(VosaeApiTest):

    @classmethod
    def setUpClass(cls):
        from organizer.models import VosaeCalendar, CalendarAclRule
        super(CalendarListResourceTest, cls).setUpClass()

        # Create a calendar which will be referenced
        new_calendar = VosaeCalendar(tenant=settings.TENANT, summary=u'My Calendar', timezone=u'Europe/Paris')
        new_calendar.acl.rules.append(CalendarAclRule(principal=settings.VOSAE_USER, role='OWNER'))
        new_calendar.save()
        cls.vosae_calendar = new_calendar

        cls.created_documents = [new_calendar]

    @classmethod
    def tearDownClass(cls):
        for document in cls.created_documents:
            document.delete()
        super(CalendarListResourceTest, cls).tearDownClass()

    def test_01_post_list(self):
        calendar_list_data = {
            'calendar': self.resourceDetailURI('vosae_calendar', unicode(self.vosae_calendar.id))
        }
        # JSON
        infos = {"app": "organizer", "resource": "CalendarListResource", "method": "post_list", "serializer": "json"}
        response = self.api_client.post(self.resourceListURI('calendar_list'), format='json', data=calendar_list_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.post(self.resourceListURI('calendar_list'), format='xml', data=calendar_list_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.post(self.resourceListURI('calendar_list'), format='yaml', data=calendar_list_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {"app": "organizer", "resource": "CalendarListResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('calendar_list'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('calendar_list'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('calendar_list'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "organizer", "resource": "CalendarListResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['summary'], u'My Calendar')
        self.assertEqual(deserialized['calendar'], self.resourceDetailURI('vosae_calendar', unicode(self.vosae_calendar.id)))
        self.assertEqual(deserialized['color'], '#44b2ae')
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
        response = self.api_client.put(self.resourceListURI('calendar_list'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('calendar_list'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('calendar_list'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        calendar_list_data = {
            'calendar': self.resourceDetailURI('vosae_calendar', unicode(self.vosae_calendar.id)),
            'color': u'#ff0000',
            'summary_override': u'Overriden Calendar'
        }
        # JSON
        infos = {"app": "organizer", "resource": "CalendarListResource", "method": "put_detail", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=calendar_list_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['summary'], u'My Calendar')
        self.assertEqual(deserialized['summary_override'], u'Overriden Calendar')
        self.assertEqual(deserialized['color'], u'#ff0000')

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=calendar_list_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=calendar_list_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_delete_detail(self):
        # JSON
        infos = {"app": "organizer", "resource": "CalendarListResource", "method": "delete_detail", "serializer": "json"}
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
        response = self.api_client.delete(self.resourceListURI('calendar_list'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('calendar_list'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('calendar_list'), format='yaml')
        self.assertHttpMethodNotAllowed(response)


class VosaeEventResourceTest(VosaeApiTest):

    @classmethod
    def setUpClass(cls):
        from organizer.models import VosaeCalendar, CalendarList, CalendarAclRule
        super(VosaeEventResourceTest, cls).setUpClass()

        # Create a calendar which will be referenced
        new_calendar = VosaeCalendar(tenant=settings.TENANT, summary=u'My Calendar', timezone=u'Europe/Paris')
        new_calendar.acl.rules.append(CalendarAclRule(principal=settings.VOSAE_USER, role='OWNER'))
        new_calendar.save()
        cls.vosae_calendar = new_calendar

        # Create an associated CalendarList
        calendar_list = CalendarList(
            tenant=settings.TENANT,
            vosae_user=settings.VOSAE_USER,
            calendar=new_calendar
        ).save()

        cls.created_documents = [new_calendar, calendar_list]

    @classmethod
    def tearDownClass(cls):
        for document in cls.created_documents:
            document.delete()
        super(VosaeEventResourceTest, cls).tearDownClass()

    def test_01_post_list(self):
        vosae_event_data.update(calendar=self.resourceDetailURI('vosae_calendar', unicode(self.vosae_calendar.id)))
        # JSON
        infos = {"app": "organizer", "resource": "VosaeEventResource", "method": "post_list", "serializer": "json"}
        # Checks failure handler
        vosae_event_fail_data = vosae_event_data.copy()
        vosae_event_fail_data['start'] = {'timezone': 'Europe/Paris'}
        response = self.api_client.post(self.resourceListURI('vosae_event'), format='json', data=vosae_event_fail_data)
        self.assertHttpBadRequest(response)
        self.assertEqual(response.content, """{"vosae_event": {"__all__": ["One of 'date' and 'datetime' must be set."]}}""")
        # Normal behavior
        response = self.api_client.post(self.resourceListURI('vosae_event'), format='json', data=vosae_event_data)
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)
        cached_data.update(json_uri=response.get('location'))

        # XML
        infos.update(serializer='xml')
        response = self.api_client.post(self.resourceListURI('vosae_event'), format='xml', data=vosae_event_data)
        self.assertHttpCreated(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(xml_uri=response.get('location'))

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.post(self.resourceListURI('vosae_event'), format='yaml', data=vosae_event_data)
        self.assertHttpCreated(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)
        cached_data.update(yaml_uri=response.get('location'))

    def test_02_get_list(self):
        # JSON
        infos = {"app": "organizer", "resource": "VosaeEventResource", "method": "get_list", "serializer": "json"}
        response = self.api_client.get(self.resourceListURI('vosae_event'), format='json')
        self.assertValidJSONResponse(response)
        self.save_test_result(infos, response)

        # XML
        infos.update(serializer='xml')
        response = self.api_client.get(self.resourceListURI('vosae_event'), format='xml')
        self.assertValidXMLResponse(response)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.get(self.resourceListURI('vosae_event'), format='yaml')
        self.assertValidYAMLResponse(response)
        self.save_test_result(infos, response)

    def test_03_get_detail(self):
        # JSON
        infos = {"app": "organizer", "resource": "VosaeEventResource", "method": "get_detail", "serializer": "json"}
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['summary'], u'My event')
        self.assertEqual(deserialized['calendar'], self.resourceDetailURI('vosae_calendar', unicode(self.vosae_calendar.id)))
        self.assertEqual(deserialized['recurrence'], None)
        self.assertEqual(deserialized['color'], None)
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
        response = self.api_client.put(self.resourceListURI('vosae_event'), format='json', data={})
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.put(self.resourceListURI('vosae_event'), format='xml', data={})
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.put(self.resourceListURI('vosae_event'), format='yaml', data={})
        self.assertHttpMethodNotAllowed(response)

    def test_05_put_detail(self):
        vosae_event_data.update(color=u'#ff0000', recurrence=u'RRULE:FREQ=YEARLY;COUNT=3')
        # JSON
        infos = {"app": "organizer", "resource": "VosaeEventResource", "method": "put_detail", "serializer": "json"}
        response = self.api_client.put(cached_data.get('json_uri'), format='json', data=vosae_event_data)
        self.assertHttpAccepted(response)
        self.assertValidJSON(response.content)
        self.save_test_result(infos, response)

        # Checks PUT
        response = self.api_client.get(cached_data.get('json_uri'), format='json')
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['summary'], u'My event')
        self.assertEqual(deserialized['recurrence'], u'RRULE:FREQ=YEARLY;COUNT=3')
        self.assertEqual(deserialized['color'], u'#ff0000')

        # XML
        infos.update(serializer='xml')
        response = self.api_client.put(cached_data.get('xml_uri'), format='xml', data=vosae_event_data)
        self.assertHttpAccepted(response)
        self.assertValidXML(response.content)
        self.save_test_result(infos, response)

        # YAML
        infos.update(serializer='yaml')
        response = self.api_client.put(cached_data.get('yaml_uri'), format='yaml', data=vosae_event_data)
        self.assertHttpAccepted(response)
        self.assertValidYAML(response.content)
        self.save_test_result(infos, response)

    def test_06_get_list_with_single_events(self):
        # JSON
        response = self.api_client.get(self.resourceListURI('vosae_event'), format='json', data={'single_events': 'true'})
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized.get('objects')), 9)  # 3 occurrences * 3 events (json/xml/yaml)

        # XML
        response = self.api_client.get(self.resourceListURI('vosae_event'), format='xml')
        self.assertValidXMLResponse(response)

        # YAML
        response = self.api_client.get(self.resourceListURI('vosae_event'), format='yaml')
        self.assertValidYAMLResponse(response)

    def test_07_get_list_with_date_range(self):
        # Original occurrence covered
        response = self.api_client.get(self.resourceListURI('vosae_event'), format='json', data={'start__gte': '2012-12-31', 'end__lt': '2013-01-07'})
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized.get('objects')), 3)  # 3 events (json/xml/yaml)

        # No occurrences covered
        response = self.api_client.get(self.resourceListURI('vosae_event'), format='json', data={'start__gte': '2100-01-01', 'end__lt': '2100-01-01'})
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized.get('objects')), 0)

        # Later occurrence covered
        response = self.api_client.get(self.resourceListURI('vosae_event'), format='json', data={'start__gte': '2014-12-29', 'end__lt': '2015-01-04'})
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(len(deserialized.get('objects')), 3)  # 3 events (json/xml/yaml)

    def test_08_delete_detail(self):
        # JSON
        infos = {"app": "organizer", "resource": "VosaeEventResource", "method": "delete_detail", "serializer": "json"}
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

    def test_09_delete_list(self):
        # JSON
        response = self.api_client.delete(self.resourceListURI('vosae_event'), format='json')
        self.assertHttpMethodNotAllowed(response)

        # XML
        response = self.api_client.delete(self.resourceListURI('vosae_event'), format='xml')
        self.assertHttpMethodNotAllowed(response)

        # YAML
        response = self.api_client.delete(self.resourceListURI('vosae_event'), format='yaml')
        self.assertHttpMethodNotAllowed(response)
