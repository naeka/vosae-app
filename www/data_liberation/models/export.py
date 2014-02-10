# -*- coding:Utf-8 -*-

from django.conf import settings
from django.utils.timezone import now as datetime_now
from mongoengine import Document, fields, NULLIFY

from core.fields import DateField


__all__ = (
    'Export',
)


class Export(Document):

    """
    Exports allows to asynchronously generate a zipped file of selected documents types in a daterange.  
    After creation, the zipfile becomes available and an e-mail is sent to the issuer.
    """
    tenant = fields.ReferenceField("Tenant", required=True)
    issuer = fields.ReferenceField("VosaeUser", required=True)
    created_at = fields.DateTimeField(required=True, default=datetime_now)
    language = fields.StringField(choices=settings.LANGUAGES, required=True, default='en')
    documents_types = fields.ListField(fields.StringField(), required=True)
    from_date = DateField()
    to_date = DateField()
    zipfile = fields.ReferenceField("VosaeFile", reverse_delete_rule=NULLIFY)

    @classmethod
    def post_save(self, sender, document, created, **kwargs):
        """
        Post save hook handler

        - Launch the async zipfile generation task if created
        """
        from data_liberation.tasks import export_documents
        if created:
            if document.zipfile:
                document.zipfile.delete()
                document.zipfile = None
            export_documents.delay(document)

    @classmethod
    def pre_delete(self, sender, document, **kwargs):
        """
        Pre delete hook handler

        - Delete of the associated zipfile.
        """
        if document.zipfile:
            document.zipfile.delete()
