# -*- coding:Utf-8 -*-

from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model
from django.utils import translation
from django.conf import settings
import re

from account.tasks import user_send_activation_email
from vosae_utils import generate_sha1

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, first_name='', last_name='', active=False, send_email=True):
        """
        A simple wrapper that creates a new :class:`User`.

        :param email:
            String containing the email address of the new user.

        :param password:
            String containing the password for the new user.

        :param first_name:
            String containing the first name for the new user.

        :param last_name:
            String containing the last name for the new user.

        :param active:
            Boolean that defines if the user requires activation by clicking
            on a link in an e-mail. Defauts to ``True``.

        :param send_email:
            Boolean that defines if the user should be send an email. You could
            set this to ``False`` when you want to create a user in your own
            code, but don't want the user to activate through email.

        :return: :class:`User` instance representing the new user.

        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=UserManager.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            is_active=active,
        )
        user.set_password(password)

        if not active:
            user.set_activation_key()

        user.save(using=self._db)

        if not active and send_email:
            user_send_activation_email.delay(user=user, language=translation.get_language())
        return user

    def create_superuser(self, email, password, first_name='', last_name=''):
        user = self.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            active=True,
            send_email=False
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def confirm_email(self, username, confirmation_key):
        """
        Confirm an email address by checking a ``confirmation_key``.

        A valid ``confirmation_key`` will set the newly wanted e-mail address
        as the current e-mail address. Returns the user after success or
        ``False`` when the confirmation key is invalid.

        :param username:
            String containing the username of the user that wants their email
            verified.

        :param confirmation_key:
            String containing the secret SHA1 that is used for verification.

        :return:
            The verified :class:`User` or ``False`` if not successful.

        """
        if SHA1_RE.search(confirmation_key):
            try:
                user = self.get(**{
                    self.model.USERNAME_FIELD: username,
                    'email_confirmation_key': confirmation_key,
                    'email_unconfirmed__isnull': False
                })
            except self.model.DoesNotExist:
                return False
            else:
                user.email = user.email_unconfirmed
                user.email_unconfirmed, user.email_confirmation_key = '', ''
                user.save(using=self._db)
                return user
        return False

    def delete_expired_users(self):
        """
        Checks for expired users and delete's the ``User`` associated with
        it. Skips if the user ``is_staff``.

        :return: A list containing the deleted users.

        """
        UserModel = get_user_model()
        deleted_users = []
        for user in UserModel.objects.filter(is_staff=False, is_active=False):
            if user.activation_key_expired():
                deleted_users.append(user)
                user.delete()
        return deleted_users

    def activate_user(self, email, activation_key):
        """
        Activate an :class:`User` by supplying a valid ``activation_key``.

        If the key is valid and an user is found, activates the user and
        return it. Also sends the ``activation_complete`` signal.

        :param email:
            String containing the email that wants to be activated.

        :param activation_key:
            String containing the secret SHA1 for a valid activation.

        :return:
            The newly activated :class:`User` or ``False`` if not successful.

        """
        if SHA1_RE.search(activation_key):
            try:
                user = self.get(**{
                    self.model.USERNAME_FIELD: email,
                    'activation_key': activation_key
                })
            except self.model.DoesNotExist:
                return False
            if not user.activation_key_expired():
                user.activation_key = settings.ACCOUNT_ACTIVATED
                user.is_active = True
                user.save(using=self._db)
                return user
        return False
