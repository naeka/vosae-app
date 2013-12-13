# -*- coding:Utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField

# Imports for Django 1.6 backported code
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
import base64

def urlsafe_base64_encode(s):
    return base64.urlsafe_b64encode(s).rstrip(b'\n=')


class UserCreationForm(forms.ModelForm):

    """A form that creates a user, with no privileges, from the given email and password."""
    error_messages = {
        'duplicate_email': _("A user with that email already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    email = forms.EmailField(
        label=_("E-mail"),
        max_length=254,
        help_text=_("Valid e-mail only."),
        error_messages={'invalid': _("This value must be a valid e-mail address.")}
    )
    password1 = forms.CharField(
        label=_("Password"),
        min_length=8,
        help_text=_("At least 8 characters."),
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        min_length=8,
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification.")
    )

    class Meta:
        model = get_user_model()
        fields = ("email",)

    def clean_email(self):
        # Since User.email is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        try:
            UserModel._default_manager.get(email=email)
        except UserModel.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class SignupForm(UserCreationForm):

    """A custom form for users registration"""
    first_name = forms.CharField(label=_("Firstname"), max_length=30, required=True)
    last_name = forms.CharField(label=_("Name"), max_length=30, required=True)

    def save(self):
        """Override the save method to save the first and last name to the user field."""
        UserModel = get_user_model()
        email, password, first_name, last_name = (
            self.cleaned_data['email'],
            self.cleaned_data['password1'],
            self.cleaned_data['first_name'],
            self.cleaned_data['last_name'],
        )
        new_user = UserModel.objects.create_user(
            email,
            password,
            first_name,
            last_name,
            not settings.ACCOUNT_ACTIVATION_REQUIRED,
            settings.ACCOUNT_ACTIVATION_REQUIRED
        )
        return new_user


class UserChangeForm(forms.ModelForm):
    email = forms.EmailField(
        label=_("E-mail"),
        max_length=254,
        help_text=_("Required. 254 characters or fewer. Valid e-mail only."),
        error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>.")
    )

    class Meta:
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class SetIdentityForm(forms.ModelForm):

    """A custom form for setting user's first_name and last_name"""
    first_name = forms.CharField(label=_("Firstname"), max_length=30, required=True)
    last_name = forms.CharField(label=_("Name"), max_length=30, required=True)

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name')


class PasswordResetForm(forms.Form):
    """
    Backported from django 1.6 for `html_email_template_name`
    To be removed as soon as we upgrade to 1.6
    """

    email = forms.EmailField(label=_("Email"), max_length=254)

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import EmailMultiAlternatives
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        users = UserModel._default_manager.filter(email__iexact=email)
        for user in users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)

            message = EmailMultiAlternatives(subject=subject, from_email=from_email, to=[user.email], body=email)

            if html_email_template_name:
                html_email = loader.render_to_string(html_email_template_name, c)
                message.attach_alternative(html_email, "text/html")
            
            message.send()
