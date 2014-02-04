# -*- coding:Utf-8 -*-

from celery.task import task
from vosae_utils import respects_language


@task
@respects_language
def user_send_activation_email(user):
    user.send_activation_email()


@task
@respects_language
def user_send_associated_to_tenant_email(user, tenant):
    user.send_associated_to_tenant_email(tenant)
