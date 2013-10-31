# -*- coding:Utf-8 -*-

from django.conf import settings
from django.shortcuts import render
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.utils.translation import activate, deactivate, get_language
from django.http import Http404
from django.template.base import TemplateDoesNotExist
import inflection


def doc_home(request):
    sample_json = """{"billing_address": null, "email": null, "fax": null, "img_logo": null, "name": "Naeka", "phone": null, "postal_address": null, "registration_info": {"resource_type": "france", "siren": "518576079", "siret": "51857607900017", "vat_number": "ABC123" }, "report_settings": {"base_color": null, "font_name": "Bariol", "font_size": 11, "force_bw": false, "language": "en" }, "slug": "naeka", "svg_logo": null, "terms": null}"""
    return render(request, 'docs/doc_home.html', {'sample_json': sample_json})


def doc_resource(request, app, resource):
    # Hack for registration infos
    if resource.endswith('_registration_info'):
        resource_name = '{0}_{1}'.format(resource[0], resource[1:])
    else:
        resource_name = resource
    tpl = 'docs/resources/{0}/{1}Resource/resource.html'.format(app, inflection.camelize(resource_name))
    try:
        return render(request, tpl, {'app': app, 'resource': resource})
    except TemplateDoesNotExist:
        raise Http404


class BaseSitemap(Sitemap):
    lastmod = None

    def location(self, obj):
        return obj[0] if isinstance(obj, tuple) else obj

    def changefreq(self, obj):
        return obj[1] if isinstance(obj, tuple) else "monthly"


class StaticSitemap(BaseSitemap):
    priority = 0.5

    def __get(self, name, obj, default=None):
        try:
            attr = getattr(self, name)
        except AttributeError:
            return default
        if callable(attr):
            return attr(obj)
        return attr

    def items(self):
        from www.urls import i18n_urlpatterns
        items = []
        init_lang = get_language()
        deactivate()
        for pattern in i18n_urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                for app in pattern.url_patterns:
                    if hasattr(app, 'url_patterns'):
                        for url in app.url_patterns:
                            if not url.name:
                                continue
                            try:
                                base = reverse(url.name)
                            except:
                                continue
                            alternates = []
                            for lang, lang_name in settings.LANGUAGES:
                                activate(lang)
                                alternate = reverse(url.name)
                                deactivate()
                                if alternate not in alternates:
                                    alternates.append((lang, alternate))
                            items.append((base, tuple(alternates)))
        activate(init_lang)
        return items

    def get_location(self, url, item):
        loc = self.__get('location', item)
        if not loc.startswith('/'):
            loc = u'/' + loc
        return "%s%s" % (url, loc)

    def get_urls(self, page=1, site=None, protocol=None):
        urls = []
        for item in self.paginator.page(page).object_list:
            priority = self.__get('priority', item, None)
            url_info = {
                'item': item,
                'location': self.get_location(settings.SITE_URL, item[0]),
                'lastmod': self.__get('lastmod', item[0], None),
                'changefreq': self.__get('changefreq', item[0], None),
                'priority': str(priority is not None and priority or ''),
                'alternate_locations': [{'lang': alternate[0], 'loc': self.get_location(settings.SITE_URL, alternate[1])} for alternate in item[1]],
            }
            urls.append(url_info)
        return urls


class DocsSitemap(BaseSitemap):
    priority = 0.4

    def __get(self, name, obj, default=None):
        try:
            attr = getattr(self, name)
        except AttributeError:
            return default
        if callable(attr):
            return attr(obj)
        return attr

    def items(self):
        return [('/docs/', (('en', '/docs/')))]

    def get_location(self, url, item):
        loc = self.__get('location', item)
        if not loc.startswith('/'):
            loc = u'/' + loc
        return "%s%s" % (url, loc)

    def get_urls(self, page=1, site=None, protocol=None):
        urls = []
        for item in self.paginator.page(page).object_list:
            priority = self.__get('priority', item, None)
            url_info = {
                'item': item,
                'location': self.get_location(settings.SITE_URL, item[0]),
                'lastmod': self.__get('lastmod', item[0], None),
                'changefreq': self.__get('changefreq', item[0], None),
                'priority': str(priority is not None and priority or ''),
            }
            urls.append(url_info)
        return urls
