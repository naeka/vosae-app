# -*- coding:Utf-8 -*-

from tastypie import fields as base_fields
from tastypie.bundle import Bundle
from tastypie_mongoengine import fields

from core.api.utils import TenantResource, ZombieMixinResource, RemoveFilesOnReplaceMixinResource
from contacts import imex as contacts_imex
from contacts.api.doc import HELP_TEXT
from contacts.tasks import entity_saved_task

from notification.mixins import NotificationAwareResourceMixin


__all__ = (
    'EntityResource',
)


class EntityResource(ZombieMixinResource, RemoveFilesOnReplaceMixinResource, NotificationAwareResourceMixin, TenantResource):
    TO_REMOVE_ON_REPLACE = ['photo']

    private = base_fields.BooleanField(
        attribute='private',
        blank=True,
        help_text=HELP_TEXT['entity']['private']
    )
    photo_source = base_fields.CharField(
        attribute='photo_source',
        null=True,
        blank=True,
        help_text=HELP_TEXT['entity']['photo_source']
    )
    gravatar_mail = base_fields.CharField(
        attribute='gravatar_mail',
        null=True,
        blank=True,
        help_text=HELP_TEXT['entity']['gravatar_mail']
    )
    photo_uri = base_fields.CharField(
        attribute='photo_uri',
        readonly=True,
        null=True,
        blank=True,
        help_text=HELP_TEXT['entity']['photo_uri']
    )
    note = base_fields.CharField(
        attribute='note',
        null=True,
        blank=True,
        help_text=HELP_TEXT['entity']['note']
    )

    addresses = fields.EmbeddedListField(
        of='contacts.api.resources.AddressResource',
        attribute='addresses',
        full=True,
        null=True,
        blank=True,
        help_text=HELP_TEXT['entity']['addresses']
    )
    emails = fields.EmbeddedListField(
        of='contacts.api.resources.EmailResource',
        attribute='emails',
        full=True,
        null=True,
        blank=True,
        help_text=HELP_TEXT['entity']['emails']
    )
    phones = fields.EmbeddedListField(
        of='contacts.api.resources.PhoneResource',
        attribute='phones',
        full=True,
        null=True,
        blank=True,
        help_text=HELP_TEXT['entity']['phones']
    )
    creator = fields.ReferenceField(
        to='core.api.resources.VosaeUserResource',
        attribute='creator',
        readonly=True,
        help_text=HELP_TEXT['entity']['creator']
    )
    photo = fields.ReferenceField(
        to='core.api.resources.VosaeFileResource',
        attribute='photo',
        null=True,
        blank=True,
        help_text=HELP_TEXT['entity']['photo']
    )

    class Meta(TenantResource.Meta):
        excludes = ('tenant', 'subscribers')

        available_imex_serializers = (contacts_imex.VCardSerializer, contacts_imex.CSVSerializer)

    def obj_create(self, bundle, **kwargs):
        """Calls the saved task here since we can extract issuer from the request"""
        bundle = super(EntityResource, self).obj_create(bundle, **kwargs)
        entity_saved_task.delay(bundle.obj, created=True, issuer=bundle.request.vosae_user)
        return bundle

    def obj_update(self, bundle, **kwargs):
        """Calls the saved task here since we can extract issuer from the request"""
        bundle = super(EntityResource, self).obj_update(bundle, **kwargs)
        entity_saved_task.delay(bundle.obj, created=False, issuer=bundle.request.vosae_user)
        return bundle

    def get_object_list(self, request):
        """
        Filters the queryset from private results.  
        Done here since we can extract caller user from the request
        """
        from mongoengine import Q
        object_list = super(EntityResource, self).get_object_list(request)
        if request and getattr(request, 'vosae_user', None):
            return object_list.filter(Q(private=False) | Q(creator=request.vosae_user))
        return object_list

    def hydrate(self, bundle):
        """On POST requests, sets the entity creator"""
        bundle = super(EntityResource, self).hydrate(bundle)
        if bundle.request.method.lower() == 'post':
            bundle.obj.creator = bundle.request.vosae_user
        return bundle

    def hydrate_private(self, bundle):
        """Ensures that the private flag can only be updated by the creator"""
        if bundle.request.method.lower() == 'put' and bundle.request.vosae_user != bundle.obj.creator:
            bundle.data['private'] = bundle.obj.private
        return bundle

    def dehydrate_photo_uri(self, bundle):
        """
        Ensures that photo URI is absolute.  
        From gravatar: nothing to do, already a secure URL
        From API: relative, prepend app endpoint to path
        """
        if bundle.data['photo_uri'] and not bundle.data['photo_uri'].startswith('http'):
            scheme = 'https' if bundle.request.is_secure() else 'http'
            return "{0}://{1}{2}".format(scheme, bundle.request.get_host(), bundle.data['photo_uri'])
        return bundle.data['photo_uri']

    def get_resource_uri(self, bundle_or_obj=None):
        if bundle_or_obj:
            if isinstance(bundle_or_obj, Bundle):
                if bundle_or_obj.obj.status != 'ACTIVE':
                    return ''
            else:
                if bundle_or_obj.status != 'ACTIVE':
                    return ''
        return super(EntityResource, self).get_resource_uri(bundle_or_obj)
