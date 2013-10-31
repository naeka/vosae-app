# -*- coding:Utf-8 -*-

from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from mongoengine import Document, fields

import uuid
import datetime
import mimetypes
import hashlib
import urllib2


__all__ = (
    'VosaeFile',
)


class VosaeFile(Document):

    """
    A wrapper for a file stored through django-storages.
    """
    tenant = fields.ReferenceField("Tenant", required=True)
    identifier = fields.StringField(required=True)
    name = fields.StringField(required=True)
    size = fields.IntField(required=True)
    sha1_checksum = fields.StringField(max_length=40, required=True)
    content_type = fields.StringField(required=True, default='application/octet-stream')
    ttl = fields.IntField(min_value=1, max_value=5 * 365 * 24 * 60)  # From 1 minute to 5 years
    delete_after = fields.DateTimeField()
    created_at = fields.DateTimeField(required=True, default=now)
    modified_at = fields.DateTimeField(required=True, default=now)
    issuer = fields.ReferenceField("VosaeUser")
    permissions = fields.ListField(fields.StringField())

    meta = {
        "indexes": ["tenant"],

        # Vosae specific
        "vosae_permissions": ("see_vosaefile", "add_vosaefile", "delete_vosaefile"),
        "vosae_mandatory_permissions": ("core_access",),
    }

    _file = None

    def __unicode__(self):
        return self.name

    @classmethod
    def pre_save(self, sender, document, **kwargs):
        """
        Pre save hook handler.
        
        - Retrieve uploaded_file.  
          If set on instanciation, present in _data, else present as attribute
        - Compute SHA1 checksum, extract content-type, size, name
        - Saves on storage backend
        """
        try:
            uploaded_file = document.uploaded_file
            del document.uploaded_file
        except AttributeError:
            try:
                uploaded_file = document._data['uploaded_file']
                del document._data['uploaded_file']
            except:
                # KeyError expected but any other except should raise this exception
                raise Exception("A VosaeFile must have an uploaded_file property while saving")

        document.size = uploaded_file.size
        document.name = uploaded_file.name
        if not document.identifier:
            document.identifier = u'{0}/{1}'.format(unicode(document.tenant.slug), unicode(uuid.uuid4()))
        if not getattr(uploaded_file, 'content_type', None):
            document.content_type = mimetypes.guess_type(document.name)[0] or 'application/octet-stream'
            uploaded_file.content_type = document.content_type

        # Checksum
        sha1 = hashlib.sha1()
        uploaded_file.seek(0)
        if uploaded_file.multiple_chunks():
            for chunk in uploaded_file.chunks():
                sha1.update(chunk)
        else:
            sha1.update(uploaded_file.read())
        document.sha1_checksum = sha1.hexdigest()
        uploaded_file.seek(0)  # Next ops seek the whole uploaded_file
        extra_headers = {'Content-Disposition': 'attachment; filename="{0}"'.format(str(urllib2.quote(document.name.encode('utf8'))))}
        default_storage.save(document.identifier, uploaded_file, extra_headers)
        document.modified_at = now()
        document.delete_after = now() + datetime.timedelta(minutes=int(document.ttl)) if document.ttl else None
        document.tenant.tenant_settings.update(set__core__quotas__used_space=int(VosaeFile.objects.filter(tenant=document.tenant).sum('size')))

    @classmethod
    def pre_delete(self, sender, document, **kwargs):
        """
        Pre delete hook handler

        - Process deletion of the GridFS file before the wrapper.
        """
        default_storage.delete(document.identifier)
        document.tenant.tenant_settings.update(set__core__quotas__used_space=int(VosaeFile.objects.filter(tenant=document.tenant).sum('size')))

    @property
    def file(self, mode='rw'):
        if not self._file and self.identifier:
            if default_storage.exists(self.identifier):
                self._file = default_storage.open(self.identifier, mode)
        return self._file

    @property
    def download_link(self):
        """
        Returns the download link.

        Has the 'attachment' header, which forces download.
        """
        return reverse("download_file", args=[self.tenant.slug, str(self.id)])

    @property
    def stream_link(self):
        """
        Returns the stream link.

        Mainly used to display images, like :class:`~contacts.models.Contact`\ s photos.
        """
        return reverse("stream_file", args=[self.tenant.slug, str(self.id)])
