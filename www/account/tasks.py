# -*- coding:Utf-8 -*-

from celery.task import task
from vosae_utils import respects_language


@task
@respects_language
def user_send_activation_email(user):
    user.send_activation_email()
