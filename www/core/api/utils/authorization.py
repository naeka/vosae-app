# -*- coding:Utf-8 -*-

from tastypie.exceptions import Unauthorized
from tastypie.authorization import Authorization


__all__ = (
    'VosaeGenericAuthorization',
    'VosaeUserAuthorization'
)


class VosaeGenericAuthorization(Authorization):

    def base_checks(self, request, model_klass):
        """
        Basic authorization checks, such as:

        - Logged-in verification
        - Application access
        - Mandatory permissions granted
        """
        # If it doesn't look like a model, we can't check permissions.
        if not model_klass or not getattr(model_klass, '_meta', None):
            return False

        # User must be logged in to check permissions.
        if not hasattr(request, 'user') or not hasattr(request, 'vosae_user'):
            return False

        # VosaeUser must have app access
        if not request.vosae_user.has_perm('core_access'):
            return False

        # Checks models mandatory perms
        if isinstance(model_klass._meta, dict) and 'vosae_mandatory_permissions' in model_klass._meta:
            for perm in model_klass._meta.get('vosae_mandatory_permissions'):
                if not request.vosae_user.has_perm(perm):
                    return False

        return model_klass

    def get_permission(self, request, access_type, model_klass):
        if isinstance(model_klass._meta, dict) and 'vosae_permissions' in model_klass._meta:
            if 'forced_class_name' in model_klass._meta:
                class_name = model_klass._meta.get('forced_class_name')
            else:
                class_name = model_klass._class_name.lower().split('.')[0]
            permission_code = '%s_%s' % (access_type, class_name)
            if permission_code in model_klass._meta.get('vosae_permissions'):
                return request.vosae_user.has_perm(permission_code)
        return None

    def get_model(self, object_list):
        if getattr(object_list, '_document', None):
            # MongoEngine Document
            return object_list._document
        else:
            try:
                # Django Model
                return object_list.model
            except:
                pass


class VosaeUserAuthorization(VosaeGenericAuthorization):

    def read_list(self, object_list, bundle):
        """Returns readable objects"""
        klass = self.base_checks(bundle.request, self.get_model(object_list))

        if klass is False:
            return []

        permission_code = self.get_permission(bundle.request, 'see', self.get_model(object_list))

        if permission_code is not None and not bundle.request.vosae_user.has_perm(permission_code):
            return []

        return object_list

    def read_detail(self, object_list, bundle):
        """Return True id readable or raises Unauthorized exception"""
        klass = self.base_checks(bundle.request, bundle.obj.__class__)

        if klass is False:
            raise Unauthorized("You are not allowed to access that resource.")

        permission_code = self.get_permission(bundle.request, 'see', bundle.obj.__class__)

        if permission_code is not None and not bundle.request.vosae_user.has_perm(permission_code):
            raise Unauthorized("You are not allowed to access that resource.")

        return True

    def create_list(self, object_list, bundle):
        """Returns the list if creation is possible"""
        klass = self.base_checks(bundle.request, self.get_model(object_list))

        if klass is False:
            return []

        permission_code = self.get_permission(bundle.request, 'add', self.get_model(object_list))

        if permission_code is not None and not bundle.request.vosae_user.has_perm(permission_code):
            return []

        return object_list

    def create_detail(self, object_list, bundle):
        """Returns True if creation is possible"""
        klass = self.base_checks(bundle.request, bundle.obj.__class__)

        if klass is False:
            raise Unauthorized("You are not allowed to access that resource.")

        permission_code = self.get_permission(bundle.request, 'add', bundle.obj.__class__)

        if permission_code is not None and not bundle.request.vosae_user.has_perm(permission_code):
            raise Unauthorized("You are not allowed to access that resource.")

        return True

    def update_list(self, object_list, bundle):
        """Returns the list if updatable"""
        klass = self.base_checks(bundle.request, self.get_model(object_list))

        if klass is False:
            return []

        permission_code = self.get_permission(bundle.request, 'change', self.get_model(object_list))

        if permission_code is not None and not bundle.request.vosae_user.has_perm(permission_code):
            return []

        return object_list

    def update_detail(self, object_list, bundle):
        """Returns True if updatable"""
        klass = self.base_checks(bundle.request, bundle.obj.__class__)

        if klass is False:
            raise Unauthorized("You are not allowed to access that resource.")

        permission_code = self.get_permission(bundle.request, 'change', bundle.obj.__class__)

        if permission_code is not None and not bundle.request.vosae_user.has_perm(permission_code):
            raise Unauthorized("You are not allowed to access that resource.")

        return True

    def delete_list(self, object_list, bundle):
        """Returns the list if deletable"""
        klass = self.base_checks(bundle.request, self.get_model(object_list))

        if klass is False:
            return []

        permission_code = self.get_permission(bundle.request, 'delete', self.get_model(object_list))

        if permission_code is not None and not bundle.request.vosae_user.has_perm(permission_code):
            return []

        return object_list

    def delete_detail(self, object_list, bundle):
        """Returns True if deletable"""
        klass = self.base_checks(bundle.request, bundle.obj.__class__)

        if klass is False:
            raise Unauthorized("You are not allowed to access that resource.")

        permission_code = self.get_permission(bundle.request, 'delete', bundle.obj.__class__)

        if permission_code is not None and not bundle.request.vosae_user.has_perm(permission_code):
            raise Unauthorized("You are not allowed to access that resource.")

        return True
