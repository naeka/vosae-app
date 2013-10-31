# -*- coding:Utf-8 -*-

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone, http
from django.template.loader import render_to_string
from django.core.mail import send_mail
import datetime

from vosae_utils import generate_sha1
from account.managers import UserManager


__all__ = (
    'ActivationMixin',
    'User',
)


class ActivationMixin(models.Model):

    """Mixin used for users activation process"""
    activation_key = models.CharField(_('activation key'), max_length=40, blank=True)
    activation_notification_send = models.BooleanField(_('notification send'), default=False, help_text=_('Designates whether this user has already got a notification about activating their account.'))
    email_unconfirmed = models.EmailField(_('unconfirmed email address'), blank=True, help_text=_('Temporary email address when the user requests an email change.'))
    email_confirmation_key = models.CharField(_('unconfirmed email verification key'), max_length=40, blank=True)

    class Meta:
        app_label = 'account'
        abstract = True

    def send_confirmation_email(self):
        """
        Sends an email to confirm the new email address.

        This method sends out two emails. One to the new email address that
        contains the ``email_confirmation_key`` which is used to verify this
        this email address with :func:`confirm_email`.

        The other email is to the old email address to let the user know that
        a request is made to change this email address.
        """
        context = {
            'user': self,
        }

        # Email to the old address
        subject_old = render_to_string('account/emails/confirmation_email_subject_old.txt', context)
        subject_old = ''.join(subject_old.splitlines())

        message_old = render_to_string('account/emails/confirmation_email_message_old.txt', context)

        send_mail(subject_old, message_old, settings.DEFAULT_FROM_EMAIL, [self.email])

        # Email to the new address
        subject_new = render_to_string('account/emails/confirmation_email_subject_new.txt', context)
        subject_new = ''.join(subject_new.splitlines())

        message_new = render_to_string('account/emails/confirmation_email_message_new.txt', context)

        send_mail(subject_new, message_new, settings.DEFAULT_FROM_EMAIL, [self.email_unconfirmed, ])

    def activation_key_expired(self):
        """
        Checks if activation key is expired.

        Returns ``True`` when the ``activation_key`` of the user is expired and
        ``False`` if the key is still valid.

        The key is expired when it's set to the value defined in
        ``ACCOUNT_ACTIVATED`` or ``activation_key_created`` is beyond the
        amount of days defined in ``ACCOUNT_ACTIVATION_DAYS``.
        """
        expiration_days = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        expiration_date = self.date_joined + expiration_days
        if self.activation_key == settings.ACCOUNT_ACTIVATED:
            return True
        if timezone.now() >= expiration_date:
            return True
        return False

    def send_activation_email(self):
        """
        Sends a activation email to the user.

        This email is send when the user wants to activate their newly created user.
        """
        context = {
            'user': self,
            'quoted_email': http.urlquote(self.email),
            'activation_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': {'name': settings.SITE_NAME, 'url': settings.SITE_URL}
        }

        subject = render_to_string('account/emails/activation_email_subject.txt', context)
        subject = ''.join(subject.splitlines())

        message = render_to_string('account/emails/activation_email_message.txt', context)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email, ])

    def change_email(self, email):
        """
        Changes the email address for a user.

        A user needs to verify this new email address before it becomes
        active. By storing the new email address in a temporary field --
        ``temporary_email`` -- we are able to set this email address after the
        user has verified it by clicking on the verification URI in the email.
        This email gets send out by ``send_verification_email``.

        :param email:
            The new email address that the user wants to use.
        """
        self.email_unconfirmed = email

        salt, hash = generate_sha1(self.email)
        self.email_confirmation_key = hash
        self.email_confirmation_key_created = timezone.now()
        self.save()

        # Send email for activation
        self.send_confirmation_email()

        return self.email_unconfirmed


class User(AbstractBaseUser, PermissionsMixin, ActivationMixin):
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False, help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True, help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    browser_language = models.CharField(_('browser language'), max_length=5, choices=settings.LANGUAGES, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        app_label = 'account'

    def get_full_name(self):
        """Returns the first_name plus the last_name, with a space in between."""
        full_name = '{0} {1}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name

    def has_identity_set(self):
        """Identity is set when both first name and last name are set"""
        if self.first_name and self.last_name:
            return True
        return False
