# -*- coding:Utf-8 -*-

from celery.task import task
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.template import Context
import zipfile

from core.models import VosaeFile
from vosae_utils import respect_language


@task()
def export_documents(export):
    from contacts.imex import get_exportable_documents as contacts_documents
    from invoicing.imex import get_exportable_documents as invoicing_documents
    with respect_language(export.language):
        archive_name = _('Vosae export.zip')
        zipped = ContentFile('', archive_name)
        f = zipfile.ZipFile(zipped, mode='w', compression=zipfile.ZIP_DEFLATED)
        for documents, path_func, doc_func in contacts_documents(export):
            for document in documents:
                f.writestr(path_func(document), doc_func(document))
        for documents, path_func, doc_func in invoicing_documents(export):
            for document in documents:
                f.writestr(path_func(document), doc_func(document))
        f.close()
        zipped.content_type = "application/zip"
        export.zipfile = VosaeFile(
            tenant=export.tenant,
            uploaded_file=zipped,
            issuer=export.issuer
        )
        export.zipfile.save()
        export.update(set__zipfile=export.zipfile)

        context = {
            'tenant': export.tenant,
            'file': export.zipfile,
            'site': {'name': settings.SITE_NAME, 'url': settings.SITE_URL}
        }

        # Email to issuer
        plaintext_context = Context(autoescape=False)  # HTML escaping not appropriate in plaintext
        subject = subject = _("Your Vosae export is available")
        text_body = render_to_string('data_liberation/emails/export_finished.txt', context, plaintext_context)
        html_body = render_to_string("data_liberation/emails/export_finished.html", context)
        message = EmailMultiAlternatives(subject=subject, from_email=settings.DEFAULT_FROM_EMAIL,
                                         to=[export.issuer.email], body=text_body)
        message.attach_alternative(html_body, "text/html")
        message.send()
