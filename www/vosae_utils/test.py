# -*- coding:Utf-8 -*-

from django.conf import settings
from django.core import urlresolvers
from django.core.exceptions import ImproperlyConfigured
from django.test import client

from tastypie.test import ResourceTestCase, TestApiClient
from tastypie.serializers import Serializer

import ConfigParser
import urlparse
import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    import yaml
    from django.core.serializers import pyyaml
except ImportError:
    yaml = None


__all__ = (
    'VosaeTestApiSerializer',
    'VosaeTestApiClient',
    'VosaeApiTest'
)


# Content is cleared before returning response, we need it
# in response to generate documentation data
class FakePayload(client.FakePayload):

    def __init__(self, content):
        self.content_data = StringIO(content)
        super(FakePayload, self).__init__(content)

client.FakePayload = FakePayload


class VosaeTestApiSerializer(Serializer):

    def to_yaml(self, data, options=None):
        options = options or {}

        if yaml is None:
            raise ImproperlyConfigured("Usage of the YAML aspects requires yaml.")

        return yaml.safe_dump(self.to_simple(data, options))


class VosaeTestApiClient(TestApiClient):

    def replace_root_tag(self, bits, root_tag):
        def rreplace(s, old, new, occurrence):
            occs = s.rsplit(old, occurrence)
            return new.join(occs)
        return rreplace(bits.replace('<response>', '<{0}>'.format(root_tag), 1), '</response>', '</{0}>'.format(root_tag), 1)

    def handle_tenant_header(self, uri):
        if uri in ['/api/v1/tenant/']:
            return {}
        return {
            'HTTP_X_TENANT': settings.TENANT.slug
        }

    def get(self, uri, **kwargs):
        kwargs.update(**self.handle_tenant_header(uri))
        return super(VosaeTestApiClient, self).get(uri, **kwargs)

    def post(self, uri, format='json', polymorph_to=None, data=None, authentication=None, **kwargs):
        kwargs.update(**self.handle_tenant_header(uri))
        content_type = self.get_content_type(format)
        kwargs['content_type'] = content_type
        kwargs['HTTP_ACCEPT'] = content_type
        if polymorph_to:
            kwargs['content_type'] += '; type={0}'.format(polymorph_to)
            kwargs['HTTP_ACCEPT'] += '; type={0}'.format(polymorph_to)

        if data is not None:
            if 'disposition' in kwargs and kwargs.get('disposition') in ('form-data',):
                kwargs['data'] = data
                kwargs.pop('disposition')
                kwargs.pop('content_type')
            else:
                kwargs['data'] = self.serializer.serialize(data, format=content_type)
                if format is 'xml':
                    kwargs['data'] = self.replace_root_tag(kwargs['data'], 'object')

        if authentication is not None:
            kwargs['HTTP_AUTHORIZATION'] = authentication

        return self.client.post(uri, **kwargs)

    def put(self, uri, format='json', polymorph_to=None, data=None, authentication=None, **kwargs):
        kwargs.update(**self.handle_tenant_header(uri))
        content_type = self.get_content_type(format)
        kwargs['content_type'] = content_type
        kwargs['HTTP_ACCEPT'] = content_type
        if polymorph_to:
            kwargs['content_type'] += '; type={0}'.format(polymorph_to)
            kwargs['HTTP_ACCEPT'] += '; type={0}'.format(polymorph_to)

        if data is not None:
            if 'disposition' in kwargs and kwargs.get('disposition') in ('form-data',):
                kwargs['data'] = data
                kwargs.pop('disposition')
                kwargs.pop('content_type')
            else:
                kwargs['data'] = self.serializer.serialize(data, format=content_type)
                if format is 'xml':
                    kwargs['data'] = self.replace_root_tag(kwargs['data'], 'object')

        if authentication is not None:
            kwargs['HTTP_AUTHORIZATION'] = authentication

        # Custom PUT because of changes made in Django 1.5
        # return self.client.put(uri, **kwargs)  # Original
        data = kwargs.pop('data', '')
        content_type = kwargs.pop('content_type', client.MULTIPART_CONTENT)
        put_data = self.client._encode_data(data, content_type)
        parsed = urlparse.urlparse(uri)
        r = {
            'CONTENT_LENGTH': len(put_data),
            'CONTENT_TYPE': content_type,
            'PATH_INFO': self.client._get_path(parsed),
            'QUERY_STRING': parsed[4],
            'REQUEST_METHOD': 'PUT',
            'wsgi.input': FakePayload(put_data)
        }
        r.update(kwargs)
        return self.client.request(**r)

    def patch(self, uri, **kwargs):
        kwargs.update(**self.handle_tenant_header(uri))
        return super(VosaeTestApiClient, self).patch(uri, **kwargs)

    def delete(self, uri, **kwargs):
        kwargs.update(**self.handle_tenant_header(uri))
        return super(VosaeTestApiClient, self).delete(uri, **kwargs)


class VosaeApiTest(ResourceTestCase):
    api_name = 'v1'

    def setUp(self):
        super(VosaeApiTest, self).setUp()
        self.api_client = VosaeTestApiClient()
        self.api_client.client.login(email='nobody@vosae.com', password='password')

    def tearDown(self):
        pass

    @classmethod
    def resourceListURI(cls, resource_name):
        return urlresolvers.reverse('api_dispatch_list', kwargs={
            'api_name': cls.api_name,
            'resource_name': resource_name
        })

    def resourcePK(self, resource_uri):
        match = urlresolvers.resolve(resource_uri)
        return match.kwargs['pk']

    @classmethod
    def resourceDetailURI(cls, resource_name, resource_pk):
        return urlresolvers.reverse('api_dispatch_detail', kwargs={
            'api_name': cls.api_name,
            'resource_name': resource_name,
            'pk': resource_pk
        })

    def fullURItoAbsoluteURI(self, uri):
        scheme, netloc, path, query, fragment = urlparse.urlsplit(uri)
        return urlparse.urlunsplit((None, None, path, query, fragment))

    def save_test_result(self, infos, response):
        if not 'VOSAE_EXPORT_TESTS_RESULTS' in os.environ:
            return
        method_dest = os.path.join(settings.SITE_ROOT, 'docs/templates/docs/resources/%(app)s/%(resource)s/methods/%(method)s/method.cfg' % infos)
        if not os.path.exists(method_dest):
            dest_dir = os.path.dirname(method_dest)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            config = ConfigParser.RawConfigParser()
        else:
            config = ConfigParser.RawConfigParser()
            config.read(method_dest)

        serializer = infos.get('serializer')
        if not config.has_section(serializer):
            config.add_section(serializer)
        config.set(serializer, 'request_method', response.request.get('REQUEST_METHOD'))
        config.set(serializer, 'request_location', response.request.get('PATH_INFO').split('/api/v1')[-1])
        if 'wsgi.input' in response.request:
            config.set(serializer, 'request_content', response.request.get('wsgi.input').content_data.read())
            config.set(serializer, 'request_content_type', response.request.get('CONTENT_TYPE'))
        if response.get('location'):
            config.set(serializer, 'response_location', response.get('location').split('/api/v1')[-1])
        config.set(serializer, 'response_content_type', response.get('content-type'))
        config.set(serializer, 'response_status_code', response.status_code)
        config.set(serializer, 'response_content', response.content)

        with open(method_dest, 'wb') as configfile:
            config.write(configfile)
