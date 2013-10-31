# -*- coding:Utf-8 -*-

from mongoengine.base import ValidationError


__all__ = (
    'AdministratorGroupIsImmutable',
)


class AdministratorGroupIsImmutable(ValidationError):

    """
    Used on :class:`~core.models.VosaeGroup` objects when trying to alter them
    without force.
    """

    def __init__(self, message="An administrator group is immutable", **kwargs):
        return super(AdministratorGroupIsImmutable, self).__init__(message, **kwargs)


class ReservedTenantSlug(Exception):

    """
    Used on :class:`~core.models.Tenant` to check if there is no conflict with urlconf
    """
    pass
