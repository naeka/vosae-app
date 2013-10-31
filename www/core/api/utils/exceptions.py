# -*- coding:Utf-8 -*-

from tastypie.exceptions import ImmediateHttpResponse
from tastypie import http


__all__ = (
    'TenantNotProvided',
    'ZombiePostConflict'
)


class TenantNotProvided(ImmediateHttpResponse):
    _response = http.HttpBadRequest('X-Tenant header must be provided')

    def __init__(self, response=None):
        if response:
            self._response = response


class ZombiePostConflict(ImmediateHttpResponse):
    _response = http.HttpConflict('This document already exists. It can be waked up thanks to the X-WakeUp header')

    def __init__(self, response=None):
        if response:
            self._response = response
