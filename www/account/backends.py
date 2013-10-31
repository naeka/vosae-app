# -*- coding:Utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class VosaeBackend(ModelBackend):

    """Wrapper of django's ModelBackend allowing to authenticate without checking password"""

    def authenticate(self, username=None, password=None, check_password=True, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
            if check_password is False or user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
