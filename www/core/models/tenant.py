# -*- coding:Utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.translation import pgettext
from django.template.defaultfilters import slugify
from mongoengine import Document, fields
from bson import ObjectId

import uuid
import pyes

from core.fields import SlugField
from core.exceptions import ReservedTenantSlug
from core.models.embedded.report_settings import ReportSettings
from core.mixins import AsyncTTLUploadsMixin
from vosae_utils import get_reserved_urlroot, get_search_settings
from vosae_settings.models import TenantSettings

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


__all__ = (
    'Tenant',
)


class RegistrationInfoField(fields.GenericEmbeddedDocumentField):

    def validate(self, value, **kwargs):
        from core.models.embedded import RegistrationInfo
        if not isinstance(value, RegistrationInfo):
            self.error("Invalid embedded document instance provided to a RegistrationInfoField")
        super(RegistrationInfoField, self).validate(value, **kwargs)


class Tenant(Document, AsyncTTLUploadsMixin):

    """
    The :class:`~core.models.Tenant` represent the tenant organization
    in the Vosae's SaaS environnement.
    """
    from contacts.models import Address
    RELATED_WITH_TTL = ['svg_logo', 'img_logo', 'terms']

    slug = SlugField(required=True, max_length=64, unique=True)
    name = fields.StringField(required=True, max_length=128)
    postal_address = fields.EmbeddedDocumentField("Address", required=True)
    billing_address = fields.EmbeddedDocumentField("Address", required=True)
    email = fields.EmailField(required=True, max_length=256)
    phone = fields.StringField(max_length=16)
    fax = fields.StringField(max_length=16)
    svg_logo = fields.ReferenceField("VosaeFile")
    img_logo = fields.ReferenceField("VosaeFile")
    logo_cache = fields.FileField()
    terms = fields.ReferenceField("VosaeFile")
    registration_info = RegistrationInfoField(required=True)
    report_settings = fields.EmbeddedDocumentField("ReportSettings", required=True, default=lambda: ReportSettings())
    tenant_settings = fields.ReferenceField("TenantSettings", required=True, default=lambda: TenantSettings())

    meta = {
        "indexes": ["slug"]
    }

    def __unicode__(self):
        return self.name

    @classmethod
    def post_init(self, sender, document, **kwargs):
        if not document.id:
            document.tenant_settings.tenant = document

    @classmethod
    def pre_save(self, sender, document, **kwargs):
        """
        If the slug does not exists (eg. on creation), it is generated.
        """
        if not document.id:
            # TenantSettings and Tenant are cross referenced
            # We need an id to reference Tenant from TenantSettings
            document.id = ObjectId()
            document.tenant_settings.save()
        if not document.slug:
            document.slug = generate_unique_slug(document, document._fields.get('slug'), document.name)

        # Manage logos
        document.manage_logos()

    @classmethod
    def pre_save_post_validation(self, sender, document, **kwargs):
        """
        The :class:`~core.models.Tenant` is associated to a Django group.
        If the group doesn't exist, it is created.
        """
        Group.objects.get_or_create(name=document.slug)

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        """
        If created, the :class:`~core.models.Tenant` should be initialized.
        """
        from core.models import VosaeGroup
        # Removed related TTL
        document.remove_related_ttl()

        if created:
            # Ensure that an index with the current search settings is present in ElasticSearch
            # Done synchronously since we can't currently chain all the related tasks from here
            conn = pyes.ES(settings.ES_SERVERS, basic_auth=settings.ES_AUTH)
            conn.ensure_index(document.slug, get_search_settings())

            # Creates an admin group
            admin_group = VosaeGroup(tenant=document, name=pgettext('group_name', 'Administrators'), is_admin=True)
            for perm, perm_data in admin_group.permissions.perms.iteritems():
                admin_group.permissions.perms[perm]['authorization'] = True
            admin_group.save()

    def delete(self, force=False, cascade=True, *args, **kwargs):
        """
        Secure hook to delete tenants.

        :param force: security, must explicitely set force to True to confirm deletion
        :param cascade: also deletes all linked documents, default to True
        """
        errors = 0
        if force:
            if cascade:
                from contacts import models as contacts_models
                from core import models as core_models
                from data_liberation import models as data_liberation_models
                from invoicing import models as invoicing_models
                from notification import models as notification_models
                from organizer import models as organizer_models
                from timeline import models as timeline_models
                from vosae_settings import models as vosae_settings_models
                models_to_delete = [
                    contacts_models.Entity, contacts_models.ContactGroup,
                    core_models.VosaeFile, core_models.VosaeGroup, core_models.VosaeUser,
                    data_liberation_models.Export,
                    invoicing_models.InvoiceBase, invoicing_models.Item, invoicing_models.Payment, invoicing_models.Tax,
                    notification_models.Notification,
                    organizer_models.Calendar, organizer_models.CalendarList, organizer_models.VosaeEvent,
                    timeline_models.TimelineEntry,
                    vosae_settings_models.TenantSettings,
                ]
                for model in models_to_delete:
                    try:
                        if model in [contacts_models.Entity, core_models.VosaeGroup, core_models.VosaeUser, invoicing_models.Tax]:
                            for obj in model.objects(tenant=self):
                                obj.delete(force=True)
                        model.objects(tenant=self).delete()
                    except:
                        errors += 1

        # Deletes the associated django Group
        try:
            Group.objects.get(name=self.slug).delete()
        except:
            errors += 1

        # Removes ElasticSearch index
        conn = pyes.ES(settings.ES_SERVERS, basic_auth=settings.ES_AUTH)
        try:
            conn.indices.delete_index(self.slug)
        except:
            errors += 1

        if errors:
            print '{0} errors occured'.format(errors)

        super(Tenant, self).delete(*args, **kwargs)

    def manage_logos(self):
        from PIL import Image
        if self.img_logo and self.img_logo.file and 'img_logo' in getattr(self, '_changed_fields', []):
            # Ensure appropriate fit
            image = Image.open(self.img_logo.file)
            if image.size[0] > 400 or image.size[1] > 160:
                image.thumbnail((400, 160), Image.ANTIALIAS)
                self.img_logo.file.seek(0)
                image.save(self.img_logo.file, image.format)
                self.img_logo.file.truncate()
                self.img_logo.file.seek(0)
            # Set the cache
            self.logo_cache.replace(self.img_logo.file)
            self.img_logo.file.seek(0)
            self.img_logo.file.close()
        elif self.svg_logo and self.svg_logo.file and 'svg_logo' in getattr(self, '_changed_fields', []):
            # Vector formats are not supported for now
            pass


def generate_unique_slug(instance, field, value):
    slug = slugify(value)
    if field.max_length:
        slug = slug[:field.max_length]

    # Try to get the original value. If not present use it.
    try:
        check_reserved_slug(slug)
        instance.__class__.objects.get(**{field.db_field: slug})
    except ReservedTenantSlug:
        pass
    except instance.__class__.DoesNotExist:
        return slug

    max_tries = 10
    if field.max_length:
        slug = slug[:field.max_length - 9]

    while max_tries > 0:
        composed_slug = '%s-%s' % (slug, uuid.uuid4().hex[:8])
        try:
            check_reserved_slug(composed_slug)
            instance.__class__.objects.get(**{field.db_field: composed_slug})
        except ReservedTenantSlug:
            pass
        except instance.__class__.DoesNotExist:
            return composed_slug
        max_tries -= 1

    # If max_tries is reached, forget value and use random uuid
    return uuid.uuid4().hex[:field.max_length]


def check_reserved_slug(slug):
    from urls import urlpatterns
    if slug in get_reserved_urlroot(urlpatterns):
        raise ReservedTenantSlug()
    return True
