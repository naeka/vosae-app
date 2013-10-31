# -*- coding:Utf-8 -*-

from django.test import simple, testcases
from django.utils import unittest
from django.conf import settings
from djcelery.contrib.test_runner import CeleryTestSuiteRunner
from decimal import Decimal

import os
import pyes
import datetime


class DummyTestResult(object):
    failures = []
    errors = []


class VosaeTestRunner(CeleryTestSuiteRunner):

    mongodb_name = 'vosae_tests'

    def setup_databases(self, **kwargs):
        from mongoengine.connection import connect, disconnect
        disconnect()
        connect(self.mongodb_name, tz_aware=True)
        print 'Creating MongoDB test database, name: {0}'.format(self.mongodb_name)
        return super(VosaeTestRunner, self).setup_databases(**kwargs)

    def _filter_suite(self, suite):
        filters = getattr(settings, 'TEST_RUNNER_FILTER', None)

        if filters is None:
            # We do NOT filter if filters are not set
            return suite

        filtered = unittest.TestSuite()

        for test in suite:
            if isinstance(test, unittest.TestSuite):
                filtered.addTests(self._filter_suite(test))
            else:
                for f in filters:
                    if test.id().startswith(f):
                        filtered.addTest(test)

        return filtered

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        if not test_labels:
            test_labels = settings.VOSAE_APPS
        suite = super(VosaeTestRunner, self).build_suite(test_labels, extra_tests=None, **kwargs)
        suite = self._filter_suite(suite)
        return simple.reorder_suite(suite, (testcases.TestCase,))

    def run_suite(self, suite, **kwargs):
        from django.contrib.auth import get_user_model

        def set_global_initial_data():
            from invoicing.models import Currency, ExchangeRate

            # Add Vosae supported currencies
            currencies_symbols = dict(settings.VOSAE_SUPPORTED_CURRENCIES).keys()
            exchange_rate_dt = datetime.datetime.now()
            for symbol in currencies_symbols:
                currency = Currency(symbol=symbol)
                for to_symbol in currencies_symbols:
                    if to_symbol == symbol:
                        continue
                    currency.rates.append(ExchangeRate(currency_to=to_symbol, datetime=exchange_rate_dt, rate=Decimal('1.00')))
                currency.save(upsert=True)

        def create_tenant(tenant_name, attached_users=[]):
            from django.contrib.auth.models import Group
            from core.models import Tenant, FRRegistrationInfo
            from contacts.models import Address
            from invoicing.models import Currency

            tenant = Tenant(
                name=tenant_name,
                email='nobody@vosae.com',
                postal_address=Address(street_address='Street address'),
                billing_address=Address(street_address='Street address'),
                registration_info=FRRegistrationInfo(
                    share_capital='100 000 EUR',
                    siret='123 456 789 012 00001',
                    rcs_number='PARIS 005',
                    vat_number='FR01234567890'
                )
            )

            # Tenant settings
            tenant.tenant_settings.invoicing.supported_currencies = [
                Currency.objects.get(symbol='EUR'),
                Currency.objects.get(symbol='USD')
            ]
            tenant.tenant_settings.invoicing.default_currency = Currency.objects.get(symbol='EUR')
            tenant.save()

            group = Group.objects.get(name=tenant.slug)
            for attached_user in attached_users:
                group.user_set.add(attached_user)
            group.save()
            return tenant

        def set_tenant_initial_data(tenant_slug, user_email):
            from core.models import Tenant, VosaeUser, VosaeGroup
            from invoicing.models import Tax

            tenant = Tenant.objects.get(slug=tenant_slug)
            # Vosae user
            vosae_user = VosaeUser(
                tenant=tenant,
                email=user_email,
                groups=[VosaeGroup.objects.get(tenant=tenant, is_admin=True)]
            ).save()

            # Taxes
            Tax(tenant=tenant, name=u'Exempt', rate=Decimal('0.00')).save()
            Tax(tenant=tenant, name=u'TVA', rate=Decimal('0.055')).save()
            Tax(tenant=tenant, name=u'TVA', rate=Decimal('0.07')).save()
            Tax(tenant=tenant, name=u'TVA', rate=Decimal('0.196')).save()
            return vosae_user

        UserModel = get_user_model()
        if not 'VOSAE_EXPORT_TESTS_RESULTS' in os.environ:
            print 'Tests \033[1mwill not\033[0m generate documentation data'
        else:
            confirm = raw_input('Tests \033[1mwill\033[0m generate documentation data. Proceed? [Y/n]: ')
            while True:
                if confirm.lower() not in ('y', '', 'n'):
                    confirm = raw_input('Please enter either "y", "n" or leave blank for default (y): ')
                    continue
                if confirm.lower() == 'n':
                    print 'Aborting...'
                    return DummyTestResult()
                break
        print 'Initializing test environnement...'
        django_user = UserModel.objects.create_user('nobody@vosae.com', 'password', active=True, send_email=False)
        set_global_initial_data()
        settings.TENANT = create_tenant('Test Company', [django_user])
        settings.VOSAE_USER = set_tenant_initial_data('test-company', 'nobody@vosae.com')

        # Should reload to get fields updated by post init tasks
        settings.TENANT.reload()
        settings.VOSAE_USER.reload()

        # Other settings overrides
        settings.STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

        # DEBUG is false by default with DjangoTestSuiteRunner
        # Cf. http://python.6.n6.nabble.com/Why-does-django-s-default-test-suite-runner-set-settings-DEBUG-False-td297023.html#a297025
        # But in some cases, for API tests, it is useful to set to True.
        # settings.DEBUG = True
        return super(VosaeTestRunner, self).run_suite(suite, **kwargs)

    def teardown_databases(self, old_config, **kwargs):
        from mongoengine.connection import get_connection, disconnect
        disconnect()
        # Removes the MongoDB database
        connection = get_connection()
        connection.drop_database(self.mongodb_name)
        print 'Dropping MongoDB test database, name: ' + self.mongodb_name

        # Removes ElasticSearch index
        conn = pyes.ES(settings.ES_SERVERS, basic_auth=settings.ES_AUTH)
        try:
            conn.indices.delete_index(settings.TENANT.slug)
            print 'Successfully removed elasticsearch index {0}'.format(settings.TENANT.slug)
        except:
            print 'elasticsearch index {0} can\'t be removed'.format(settings.TENANT.slug)
        super(VosaeTestRunner, self).teardown_databases(old_config, **kwargs)
