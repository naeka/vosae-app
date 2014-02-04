# -*- coding:Utf-8 -*-

from mongoengine import Document, fields, signals
from django.utils import translation
from django.contrib.auth import get_user_model
from django_gravatar.helpers import get_gravatar_url

from vosae_utils import SearchDocumentMixin
from pyes import mappings as search_mappings

from account.tasks import user_send_associated_to_tenant_email

from core.models.embedded.vosae_permissions import VosaePermissions
from core.models.embedded.vosae_user_settings import VosaeUserSettings
from core.mixins import ZombieMixin
from core.tasks import es_document_index, es_document_deindex


__all__ = (
    'VosaeUser',
)


class VosaeUser(ZombieMixin, Document, SearchDocumentMixin):

    """
    A user class linking :class:`~core.models.Tenant` to Django's user
    in our SaaS environnement.
    """
    STATUSES = ('ACTIVE', 'DISABLED', 'DELETED')
    DELETE_STATUS = 'DELETED'

    tenant = fields.ReferenceField("Tenant", required=True)
    email = fields.EmailField(unique_with="tenant", required=True)
    status = fields.StringField(choices=STATUSES, required=True, default=ZombieMixin.DEFAULT_STATUS)
    groups = fields.ListField(fields.ReferenceField("VosaeGroup"))
    specific_permissions = fields.DictField()
    permissions = fields.EmbeddedDocumentField("VosaePermissions", default=lambda: VosaePermissions())
    settings = fields.EmbeddedDocumentField("VosaeUserSettings", default=lambda: VosaeUserSettings())

    meta = {
        "indexes": ["tenant", "email", "status"],

        # Vosae specific
        "vosae_permissions": ("see_vosaeuser", "add_vosaeuser", "change_vosaeuser", "delete_vosaeuser"),
        "vosae_mandatory_permissions": ("core_access", "change_appconf"),
    }

    class Meta():
        document_type = 'user'
        document_boost = 2 / 3.0
        fields = [
            search_mappings.StringField(name="full_name", boost=document_boost * 3.0, store=True, term_vector="with_positions_offsets", index="analyzed"),
            search_mappings.StringField(name="email", boost=document_boost * 2.7, store=True, term_vector="with_positions_offsets", index="analyzed"),
        ]

    def __unicode__(self):
        return u'%s (%s)' % (self.email, self.tenant)

    def get_search_kwargs(self):
        return {
            'full_name': self.get_full_name(),
            'email': self.email
        }

    @classmethod
    def get_indexable_documents(cls, **kwargs):
        return cls.objects.filter(status='ACTIVE', **kwargs)

    @classmethod
    def pre_save(self, sender, document, **kwargs):
        """
        Merge groups and own permissions and refresh cache
        """
        document.permissions.merge_groups_and_user(document.groups, document)
        document.permissions.refresh_acquired()

    @classmethod
    def pre_save_post_validation(self, sender, document, **kwargs):
        """
        When creating a :class:`~core.models.VosaeUser` we check for the django user corresponding mail.

        If user does not exist, it will be created.
        """
        from django.contrib.auth.models import Group
        if not document.id:
            UserModel = get_user_model()
            try:
                user = UserModel._default_manager.get(email=document.email)
                if not user.is_active and not user.activation_key:
                    user.set_activation_key()
                    user.save()
                user_send_associated_to_tenant_email.delay(user=user, tenant=document.tenant, language=translation.get_language())
            except UserModel.DoesNotExist:
                user = UserModel.objects.create_user(document.email)
            group = Group.objects.get(name=document.tenant.slug)
            group.user_set.add(user)
            group.save()

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        """
        Post save hook handler

        - Initialize user on creation
        - Index user in elasticsearch
        """
        from core.tasks import vosae_user_init
        if created:
            vosae_user_init.delay(document)

        # Index user in elasticsearch
        es_document_index.delay(document)

    @classmethod
    def post_delete(self, sender, document, **kwargs):
        """
        Post delete hook handler

        - Removes the django user from the django group
        - De-index user from elasticsearch
        """
        from django.contrib.auth.models import Group
        UserModel = get_user_model()

        # Removes the django user from the django group
        user = UserModel._default_manager.get(email=document.email)
        group = Group.objects.get(name=document.tenant.slug)
        group.user_set.remove(user)
        group.save()

        # De-index document from Elastic Search
        es_document_deindex.delay(document)

    @property
    def photo_uri(self):
        """
        Return the photo URI (if available).
        """
        if self.settings.gravatar_email:
            return get_gravatar_url(self.settings.gravatar_email)
        else:
            return None

    def has_perm(self, perm):
        """
        True if the :class:`~core.models.VosaeUser` has the specified permission and
        if the :class:`~core.models.Tenant` has the corresponding subscription active.
        """
        if not perm in self.permissions.perms:
            return True
        if self.permissions.perms[perm]["authorization"]:
            return True
        return False

    def is_active(self):
        return self.status == 'ACTIVE'

    def get_full_name(self):
        """
        Return the :class:`~core.models.VosaeUser` full name, based on the Django user.
        """
        UserModel = get_user_model()
        try:
            user = UserModel._default_manager.get(email=self.email)
            return user.get_full_name()
        except:
            return None

    def get_permissions(self):
        perms = {}
        for perm_name, perm_data in self.permissions.perms.iteritems():
            perms[perm_name] = perm_data['authorization']
        return perms

    def get_language(self):
        if self.settings.language_code:
            return self.settings.language_code
        else:
            UserModel = get_user_model()
            user = UserModel._default_manager.get(email=self.email)
            if user.browser_language:
                return user.browser_language
            return 'en'
