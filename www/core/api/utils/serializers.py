# -*- coding:Utf-8 -*-

from tastypie.serializers import Serializer
from tastypie.utils import format_datetime


__all__ = (
    'VosaeSerializer',
)


class VosaeSerializer(Serializer):

    def format_datetime(self, data):
        """
        A hook to control how datetimes are formatted RESPECTING TIMEZONES.
        """
        if self.datetime_formatting == 'rfc-2822':
            return format_datetime(data)
        return data.isoformat()
