# -*- coding:Utf-8 -*-

from django.conf import settings
from django.utils.encoding import force_unicode
from django.contrib.staticfiles.storage import CachedFilesMixin

from boto.s3.key import Key
from storages.backends.s3boto import S3BotoStorage

import mimetypes


__all__ = (
    'VosaeS3BotoStorage',
    'S3CachedStorage'
)


class VosaeS3BotoStorage(S3BotoStorage):

    def _save(self, name, content, extra_headers={}):
        cleaned_name = self._clean_name(name)
        name = self._normalize_name(cleaned_name)
        headers = self.headers.copy()
        content_type = getattr(content, 'content_type', mimetypes.guess_type(name)[0] or Key.DefaultContentType)

        if self.gzip and content_type in self.gzip_content_types:
            content = self._compress_content(content)
            headers.update({'Content-Encoding': 'gzip'})

        content.name = cleaned_name
        k = self.bucket.get_key(self._encode_name(name))
        if not k:
            k = self.bucket.new_key(self._encode_name(name))

        k.set_metadata('Content-Type', content_type)
        for header, value in extra_headers.items():
            k.set_metadata(header, value)

        k.set_contents_from_file(content, headers=headers, policy=self.default_acl, reduced_redundancy=self.reduced_redundancy)
        return cleaned_name

    def save(self, name, content, extra_headers={}):
        """
        Saves new content to the file specified by name. The content should be a
        proper File object, ready to be read from the beginning.
        """
        # Get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name

        name = self.get_available_name(name)
        name = self._save(name, content, extra_headers)

        # Store filenames with forward slashes, even on Windows
        return force_unicode(name.replace('\\', '/'))


class S3CachedStorage(CachedFilesMixin, S3BotoStorage):

    def __init__(self, *args, **kwargs):
        kwargs.update(bucket=settings.AWS_STATIC_BUCKET_NAME)
        super(S3CachedStorage, self).__init__(*args, **kwargs)
