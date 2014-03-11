# -*- coding:Utf-8 -*-

from django.utils.translation import ugettext as _
from django.utils.timezone import now
from celery.task import periodic_task, task
from celery.schedules import crontab
from decimal import Decimal
from datetime import date

import time
import pyes

from vosae_utils import respect_language


@periodic_task(run_every=crontab(minute=5))
def fetch_currencies():
    from invoicing.models import Currency
    Currency.refresh_currencies()


@periodic_task(run_every=crontab(minute='*/15'))
def delete_expired_files():
    from core.models import VosaeFile
    for vosae_file in VosaeFile.objects(delete_after__lte=now()):
        vosae_file.delete()


@task()
def cache_changed_permissions(vosae_group):
    from core.models import VosaeUser
    users = VosaeUser.objects.filter(groups__in=[vosae_group])
    for user in users:
        user.permissions.merge_groups_and_user(user.groups, user)
        user.permissions.refresh_acquired()
        user.save()


@task()
def fill_tenant_initial_data(tenant, language_code):
    """
    This task creates inital data when a new :class:`~core.models.Tenant` is created
    """
    from core.models import VosaeUser
    from contacts.models import Contact, Organization, Email, Address
    from invoicing.models import Item, Tax, Currency

    with respect_language(language_code):
        initial_vosae_user = VosaeUser.objects.get(tenant=tenant)

        # Creates default taxes, based on registration country
        for tax_percent, tax_name in tenant.registration_info.get_default_taxes():
            Tax(tenant=tenant, name=tax_name, rate=tax_percent).save()

        # Creates a shared organization
        Organization(
            tenant=tenant,
            creator=initial_vosae_user,
            corporate_name=u'Vosae',
            emails=[
                Email(type=u'WORK', email=u'support@vosae.com')
            ],
            addresses=[
                Address(type=u'WORK', street_address=u'35 Rue Lesdiguières', postal_code=u'38000', city=u'Grenoble', country=u'France')
            ],
            note=_('We\'d like to make it right'),
            private=False
        ).save()

        # Creates a shared contact
        Contact(
            tenant=tenant,
            creator=initial_vosae_user,
            name=_('Support'),
            firstname=u'Vosae',
            role=_('The best support'),
            emails=[
                Email(type=u'WORK', email=u'support@vosae.com')
            ],
            organization=Organization.objects.get(tenant=tenant, corporate_name=u'Vosae'),
            private=False
        ).save()

        # Creates an item
        Item(
            tenant=tenant,
            reference=_('TEST-ITEM'),
            description=_('Test item'),
            unit_price=Decimal('1000'),
            currency=Currency.objects.get(symbol='EUR'),
            tax=Tax.objects.filter(tenant=tenant).first(),
            type=u'SERVICE'
        ).save()


@task()
def fill_user_initial_data(vosae_user, language_code):
    """
    This task creates inital data when a new :class:`~core.models.VosaeUser` is created
    """

    from organizer.models import VosaeCalendar, CalendarList, CalendarAclRule, VosaeEvent, EventDateTime

    with respect_language(language_code):
        # Creates a personal Calendar and an associated CalendarList
        calendar = VosaeCalendar(tenant=vosae_user.tenant, summary=_('My calendar'))
        calendar.acl.rules.append(CalendarAclRule(principal=vosae_user, role=u'OWNER'))
        calendar.save()
        CalendarList(
            tenant=vosae_user.tenant,
            vosae_user=vosae_user,
            calendar=calendar,
            selected=True
        ).save()

        # Creates an Event
        VosaeEvent(
            tenant=vosae_user.tenant,
            calendar=calendar,
            summary=_('I joined %(tenant)s on Vosae') % {'tenant': vosae_user.tenant},
            description=_('This is the most amazing day of my life, I joined %(tenant)s on Vosae') % {'tenant': vosae_user.tenant.name},
            creator=vosae_user,
            organizer=vosae_user,
            start=EventDateTime(date=date.today()),
            end=EventDateTime(date=date.today())
        ).save()


@task()
def vosae_user_init(vosae_user):
    from django_gravatar.helpers import has_gravatar

    # Checks for gravatar email
    if not vosae_user.settings.gravatar_email:
        if has_gravatar(vosae_user.email):
            vosae_user.settings.gravatar_email = vosae_user.email
            vosae_user.update(set__settings__gravatar_email=vosae_user.email)


@task()
def es_document_index(document):
    from vosae_utils import SearchDocumentMixin
    if not isinstance(document, SearchDocumentMixin):
        raise TypeError('Document must be a subclass of SearchDocumentMixin')
    try:
        document.es_index()
    except pyes.exceptions.SearchPhaseExecutionException:
        time.sleep(1)
        document.es_index()


@task()
def es_document_deindex(document):
    from vosae_utils import SearchDocumentMixin
    if not isinstance(document, SearchDocumentMixin):
        raise TypeError('Document must be a subclass of SearchDocumentMixin')
    document.es_deindex()
