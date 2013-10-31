# -*- coding:Utf-8 -*-

from django.conf.urls import url
from dateutil.parser import parse
from pymongo.errors import InvalidOperation, OperationFailure

from tastypie import http, fields as base_fields
from tastypie.utils import trailing_slash

from core.api.utils import TenantResource
from vosae_statistics.models import Statistics


__all__ = (
    'StatisticsResource',
)


class StatisticsResource(TenantResource):
    pipeline = base_fields.ListField()

    class Meta(TenantResource.Meta):
        list_allowed_methods = ('post',)
        detail_allowed_methods = ()
        include_resource_uri = False

    def base_urls(self):
        """The standard URLs this ``Resource`` should respond to."""
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_statistics'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
        ]

    def get_statistics(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)

        try:
            body = request.body
            deserialized = self.deserialize(request, body, format=request.META.get('CONTENT_TYPE', 'application/json'))
            deserialized = self.alter_deserialized_detail_data(request, deserialized)
        except ValueError as e:
            # Serialization errors -> relayed to API users
            return self.create_response(request, e, response_class=http.HttpBadRequest)
        except:
            # Other errors
            return http.HttpBadRequest()

        try:
            result = Statistics._get_collection().aggregate(deserialized.get('pipeline')).get('result')
        except (InvalidOperation, OperationFailure) as e:
            # Aggregation pipeline operation errors -> relayed to API users
            return self.create_response(request, e, response_class=http.HttpBadRequest)
        except:
            # Other errors
            return http.HttpBadRequest()

        self.log_throttled_access(request)

        paginator = self._meta.paginator_class(request.GET, result, resource_uri=self.get_resource_uri(), limit=self._meta.limit)
        to_be_serialized = paginator.page()
        return self.create_response(request, to_be_serialized, response_class=http.HttpAccepted)

    def alter_deserialized_detail_data(self, request, data):
        data = super(StatisticsResource, self).alter_deserialized_detail_data(request, data)
        for pos, action in enumerate(data['pipeline']):
            if '$match' in action and 'date' in action['$match']:
                if isinstance(action['$match']['date'], basestring):
                    try:
                        data['pipeline'][pos]['$match']['date'] = parse(action['$match']['date'], ignoretz=True)
                    except:
                        pass
                elif isinstance(action['$match']['date'], dict):
                    for k, v in action['$match']['date'].items():
                        try:
                            data['pipeline'][pos]['$match']['date'][k] = parse(v, ignoretz=True)
                        except:
                            pass
        data['pipeline'].insert(0, {u'$match': {u'tenant': request.tenant.id}})
        return data

    def get_schema(self, request, **kwargs):
        """Overriden to avoid any error since there is no object_class defined for VosaeSearch"""
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        self.log_throttled_access(request)
        return self.create_response(request, self.build_schema())
