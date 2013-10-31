# -*- coding:Utf-8 -*-

from django.conf.urls import url
from django.conf import settings

from tastypie import http
from tastypie.utils import trailing_slash

from core.api.utils import TenantResource


__all__ = (
    'VosaeSearchResource',
)


class VosaeSearchResource(TenantResource):

    class Meta(TenantResource.Meta):
        resource_name = 'search'
        list_allowed_methods = ('get',)
        detail_allowed_methods = ()
        include_resource_uri = False

    def base_urls(self):
        """The standard URLs this ``Resource`` should respond to."""
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
        ]

    def get_search(self, request, **kwargs):
        """
        Execute a search query to elasticsearch

        Request parameters are:
        - `q`: string query
        - `types`: set of document types (`contact`, `organization`, `invoice`, ...)

        A minimum of 2 chars are required for the query to be processed (wildcards excluded).
        """
        import re
        import pyes
        from pyes.query import Search, StringQuery

        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        try:
            # Tenant (slug) must be present
            tenant = request.tenant.slug
            # By default, search is made among all types, can be overriden passing a types argument
            doc_types = request.GET.getlist('types')
            # The 'q' parameter represents the query
            query = request.GET.get('q')
            # The query must be a string and composed by at least 2 chars (ES wildcards excluded)
            assert (isinstance(query, basestring) and len(re.sub('[?*]', '', query)) >= 2)
        except:
            return http.HttpBadRequest()

        try:
            conn = pyes.ES(settings.ES_SERVERS, basic_auth=settings.ES_AUTH)
            q = Search(StringQuery(query))
            resultset = conn.search(q, indices=tenant, doc_types=u",".join(doc_types) if doc_types else None)
            searched_items = []
            for res in resultset:
                res.update({
                    'id': res._meta['id'],
                    'resource_type': res._meta['type'],
                    'score': res._meta['score']
                })
                searched_items.append(res)
        except:
            return http.HttpBadRequest()

        self.log_throttled_access(request)

        paginator = self._meta.paginator_class(request.GET, searched_items, resource_uri=self.get_resource_uri(), limit=self._meta.limit)
        to_be_serialized = paginator.page()
        return self.create_response(request, to_be_serialized, response_class=http.HttpResponse)

    def get_schema(self, request, **kwargs):
        """Overriden to avoid any error since there is no object_class defined for VosaeSearch"""
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        self.log_throttled_access(request)
        return self.create_response(request, self.build_schema())
