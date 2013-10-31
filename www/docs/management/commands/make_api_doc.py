# -*- coding:Utf-8 -*-

from django.core.management.base import BaseCommand
from django.template import Context, Template
from django.conf import settings
from optparse import make_option
from collections import OrderedDict
from mongoengine import EmbeddedDocument
from inflection import humanize
import os
import ConfigParser

from www import api as api_module
from docs.templatetags.status_code import status_code


class Command(BaseCommand):
    help = 'Generate a documentation for every API resource, based on their schemas.'
    option_list = BaseCommand.option_list + (
        make_option('-n', '--api-name',
            action='store',
            dest='api_name',
            default='v1',
            help='Api name, such as "v1", defined as "v1_api" in api.py'
        ),
    )

    def handle(self, *args, **options):
        api_name = '%s_api' % options.get('api_name')
        api = getattr(api_module, api_name)

        doc_apps = ('account', 'contacts', 'core', 'invoicing', 'organizer')
        endpoint_resources = [res.__class__ for res in api._registry.values()]
        apps = {}

        for app in doc_apps:
            app_resources = __import__('%s.api.resources' % app, fromlist=['%s.api' % app])
            for resource_name in app_resources.__all__:
                resource = getattr(app_resources, resource_name)
                if not app in apps:
                    apps[app] = {'endpoints': [], 'subsidiary': []}
                if resource in endpoint_resources:
                    apps[app]['endpoints'].append(resource)
                else:
                    object_class = getattr(resource.Meta, 'object_class', None)
                    if object_class and issubclass(object_class, EmbeddedDocument):
                        apps[app]['subsidiary'].append(resource)
            apps[app]['endpoints'].sort(key=lambda resource: resource.__name__)
            apps[app]['subsidiary'].sort(key=lambda resource: resource.__name__)

        for app_name, app in apps.items():
            for resource in app['endpoints']:
                self.gen_resource_doc(app_name, resource, True, options)
            for resource in app['subsidiary']:
                self.gen_resource_doc(app_name, resource, False, options)

        self.gen_resource_index(apps)

    def gen_resource_doc(self, app_name, resource, is_endpoint, options):
        try:
            schema = resource(options.get('api_name')).build_schema()
        except:
            print "Error while processing %s" % resource.__name__
            return

        path = os.path.dirname(__file__)
        resource_template = Template(open(path + "/make_api_doc_templates/resource.html").read())
        endpoint_infos_template = Template(open(path + "/make_api_doc_templates/endpoint_informations.html").read())
        spec_template = Template(open(path + "/make_api_doc_templates/spec.html").read())
        methods_template = Template(open(path + "/make_api_doc_templates/methods.html").read())
        method_template = Template(open(path + "/make_api_doc_templates/method.html").read())
        sample_template = Template(open(path + "/make_api_doc_templates/sample.html").read())
        resource_dest = os.path.join(settings.SITE_ROOT, 'docs/templates/docs/resources/%(app)s/%(resource)s/resource.html' % {"app": app_name, "resource": resource.__name__})
        endpoint_infos_dest = os.path.join(settings.SITE_ROOT, 'docs/templates/docs/resources/%(app)s/%(resource)s/endpoint_informations.html' % {"app": app_name, "resource": resource.__name__})
        spec_dest = os.path.join(settings.SITE_ROOT, 'docs/templates/docs/resources/%(app)s/%(resource)s/spec.html' % {"app": app_name, "resource": resource.__name__})
        methods_dir = os.path.join(settings.SITE_ROOT, 'docs/templates/docs/resources/%(app)s/%(resource)s/methods' % {"app": app_name, "resource": resource.__name__})
        methods_dest = os.path.join(methods_dir, 'methods.html')
        dest_dir = os.path.dirname(resource_dest)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        resource_methods = OrderedDict()
        if is_endpoint:
            if not os.path.exists(methods_dir):
                os.makedirs(methods_dir)
            method_order = ('post_list', 'get_list', 'get_detail', 'put_list', 'put_detail', 'delete_detail', 'delete_list')
            allowed_methods_unsorted = ['%s_list' % m for m in schema['allowed_list_http_methods']] + ['%s_detail' % m for m in schema['allowed_detail_http_methods']]
            allowed_methods = []
            specific_methods = []
            for method in method_order:
                if method in allowed_methods_unsorted:
                    allowed_methods.append(method)
            if 'detail_specific_methods' in schema:
                specific_methods = schema['detail_specific_methods']
                method_order += specific_methods
                allowed_methods += specific_methods
            for method in allowed_methods:
                path = os.path.join(settings.SITE_ROOT, 'docs/templates/docs/resources/%(app)s/%(resource)s/methods/%(method)s/method.cfg' % {"app": app_name, "resource": resource.__name__, 'method': method})
                if (os.path.exists(path)):
                    resource_methods[method] = OrderedDict()
                    config = ConfigParser.RawConfigParser()
                    config.read(path)
                    serializer_order = ('json', 'xml', 'yaml')
                    serializers_unsorted = config.sections()
                    serializers = []
                    for serializer in serializer_order:
                        if serializer in serializers_unsorted:
                            serializers.append(serializer)
                    for serializer in serializers:
                        resource_methods[method][serializer] = {}
                        for key, value in config.items(serializer):
                            resource_methods[method][serializer][key] = value
                        resource_methods[method][serializer]['request_headers'] = get_request_headers(resource_methods[method][serializer])
                        resource_methods[method][serializer]['response_headers'] = get_response_headers(resource_methods[method][serializer])

            for method in method_order:
                if method not in resource_methods:
                    continue
                method_root = os.path.join(methods_dir, method)
                if method in specific_methods:
                    method_title = '{0} /{1}/:id/'.format(humanize(method), resource._meta.resource_name)
                else:
                    method_type = method.replace('_list', '').replace('_detail', '')
                    if method.endswith('_list'):
                        method_title = '{0} /{1}/'.format(method_type.upper(), resource._meta.resource_name)
                    else:
                        method_title = '{0} /{1}/:id/'.format(method_type.upper(), resource._meta.resource_name)
                sample_dest = os.path.join(method_root, 'sample.html')
                sample_html = sample_template.render(Context({
                    'method': method,
                    'resource_method': resource_methods[method]
                }))
                sample_file = open(sample_dest, 'w')
                sample_file.write(sample_html)

                method_dest = os.path.join(method_root, 'method.html')
                method_html = method_template.render(Context({
                    'sample_tpl': 'docs/resources/{0}/{1}/methods/{2}/sample.html'.format(app_name, resource.__name__, method),
                    'method_title': method_title,
                    'resource_methods': resource_methods
                }))
                if os.path.exists(method_dest + '.LAST_GEN'):
                    do_three_way_merge(method_dest, method_html, options)
                else:
                    method_file = open(method_dest, 'w')
                    method_file.write(method_html)
                    method_file.close()
                    method_file_last_gen = open(method_dest + '.LAST_GEN', 'w')
                    method_file_last_gen.write(method_html)
                    method_file_last_gen.close()

            methods_html = methods_template.render(Context({
                'resource_methods': resource_methods,
                'method_dir': 'docs/resources/{0}/{1}/methods'.format(app_name, resource.__name__)
            }))
            methods_file = open(methods_dest, 'w')
            methods_file.write(methods_html)
            methods_file.close()

        context = {
            'app_name': app_name,
            'resource': resource,
            'resource_class': resource.__name__,
            'resource_name': resource._meta.resource_name,
            'resource_meta': schema,
            'ordered_fields': OrderedDict(sorted(schema['fields'].items())),
            'is_endpoint': is_endpoint,
        }

        resource_context = context.copy()
        if len(resource_methods):
            resource_context.update(has_methods=True)
        resource_html = resource_template.render(Context(resource_context))
        if os.path.exists(resource_dest + '.LAST_GEN'):
            do_three_way_merge(resource_dest, resource_html, options)
        else:
            resource_file = open(resource_dest, 'w')
            resource_file.write(resource_html)
            resource_file.close()
            resource_file_last_gen = open(resource_dest + '.LAST_GEN', 'w')
            resource_file_last_gen.write(resource_html)
            resource_file_last_gen.close()

        if is_endpoint:
            endpoint_infos_html = endpoint_infos_template.render(Context(context))
            endpoint_infos_file = open(endpoint_infos_dest, 'w')
            endpoint_infos_file.write(endpoint_infos_html)
            endpoint_infos_file.close()

        spec_html = spec_template.render(Context(context))
        spec_file = open(spec_dest, 'w')
        spec_file.write(spec_html)
        spec_file.close()

    def gen_resource_index(self, apps):
        path = os.path.dirname(__file__)
        template = Template(open(path + '/make_api_doc_templates/resource_list.html').read())
        dest = os.path.join(settings.SITE_ROOT, 'docs/templates/docs/resource_list.html')
        html = template.render(Context({
            'apps': apps
        }))
        res_file = open(dest, 'w')
        res_file.write(html)
        res_file.close()


def get_request_headers(method):
    headers = u'{0} {1}'.format(method['request_method'], method['request_location'])
    if 'request_content_type' in method:
        headers += u'\nContent-Type: {0}'.format(method['request_content_type'])
    return headers


def get_response_headers(method):
    headers = status_code(method['response_status_code'])
    if 'response_content_type' in method:
        headers += u'\nContent-Type: {0}'.format(method['response_content_type'])
    if 'response_location' in method:
        headers += u'\nLocation: {0}'.format(method['response_location'])
    return headers


def do_three_way_merge(file_dest, file_html, options):
    file_dest_last = file_dest + '.LAST_GEN'
    file_dest_new = file_dest + '.NEW_GEN'
    file_dest_new_gen = open(file_dest_new, 'w')
    file_dest_new_gen.write(file_html)
    file_dest_new_gen.close()
    try:
        merged = os.popen('diff3 -am {0} {1} {2}'.format(file_dest, file_dest_last, file_dest_new))
        buf = merged.read()
        file_dest = open(file_dest, 'w')
        file_dest.write(buf)
        file_dest.close()
        file_dest_last_gen = open(file_dest_last, 'w')
        file_dest_last_gen.write(file_html)
        file_dest_last_gen.close()
        os.remove(file_dest_new)
    except:
        print 'Error encountered while merging {0}'.format(file_dest)
        print 'Please, resolve this manually'
