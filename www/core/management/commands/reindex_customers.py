# -*- coding:Utf-8 -*-

from django.core.management.base import BaseCommand
from django.conf import settings
from optparse import make_option
import sys
import pyes

from core.models import Tenant
from vosae_utils import get_search_models, get_search_settings


class Command(BaseCommand):
    help = 'Reindex tenants documents'
    option_list = BaseCommand.option_list + (
        make_option('-c', '--tenant',
                    action='store',
                    dest='tenant',
                    default=None,
                    help='Reindex a specific tenant, must provide its slug.'
                    ),
    )

    def handle(self, *args, **options):
        kwargs = {}
        if options.get('tenant'):
            kwargs.update(slug=options.get('tenant'))
        tenants = Tenant.objects.filter(**kwargs)
        tenants_count = tenants.count()
        search_models = get_search_models()
        search_settings = get_search_settings()
        conn = pyes.ES(settings.ES_SERVERS, basic_auth=settings.ES_AUTH)
        if tenants_count == 1:
            print 'Reindexing tenant {0}'.format(tenants[0].name)
        else:
            print 'Reindexing {0} tenants'.format(tenants_count)

        # Processing each tenant independently
        for tenant in tenants:
            try:
                # Ensure index mapping
                conn.ensure_index(tenant.slug, search_settings, clear=True)

                # Data indexation
                for name, cls in search_models:
                    kwargs = {'tenant': tenant}
                    obj_list = cls.get_indexable_documents(**kwargs)

                    if options.get('verbosity') is '2':
                        sys.stdout.write("\rIndexing %d %ss..." % (len(obj_list), name))
                        sys.stdout.flush()

                    for doc in obj_list:
                        try:
                            doc.es_index()
                        except Exception as e:
                            print u'\r{0}'.format(e)
                if options.get('verbosity') is '2':
                    print unicode('\r[{0}]'.format(tenant.slug)).ljust(30) + ": OK"
            except Exception as e:
                print 'An error occured with tenant {0}:'.format(tenant.slug)
                print e
