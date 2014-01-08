# -*- coding:Utf-8 -*-

import datetime

from django.utils.timezone import now
from django.template.loader import render_to_string
from django.template import Context
from django.conf import settings
from django.core.mail import EmailMessage, get_connection

from celery.task import task, periodic_task
from celery.schedules import crontab

from vosae_utils import respects_language


@task
@respects_language
def user_send_activation_email(user):
    user.send_activation_email()

@periodic_task(run_every=crontab(minute=0, hour='*/1'))
@respects_language
def user_send_inactive_email():
    from account.models import User

    for user in User.objects.filter(is_active=False, date_joined__gte=now() - datetime.timedelta(days=1, hours=1), date_joined__lte=now() - datetime.timedelta(days=1)):

        context = {
            'user': user,
            'site': {'name': settings.SITE_NAME, 'url': settings.SITE_URL}
        }
        # Send mails
        connection = get_connection()
        plaintext_context = Context(autoescape=False)  # HTML escaping not appropriate in plaintext
        subject = render_to_string('account/emails/inactive_email_subject.txt', context, plaintext_context)
        subject = ''.join(subject.splitlines())
        text_body = render_to_string('account/emails/inactive_email_message.txt', context, plaintext_context)

        message = EmailMessage(subject=subject, from_email="maxime@vosae.com", to=[user.email], body=text_body, connection=connection)
        message.preserve_recipients = False # Useful for Mandrill
        message.send()
