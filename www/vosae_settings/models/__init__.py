# -*- coding:Utf-8 -*-

from mongoengine import fields, Document, signals

from vosae_settings.models.core_settings import CoreSettings
from vosae_settings.models.invoicing_settings import InvoicingSettings, VosaeInvoicingMixin


__all__ = (
    'TenantSettings',
)


class TenantSettings(Document, VosaeInvoicingMixin):

    """
    The main settings object.

    Inherits from all custom settings: an application which requires specific settings
    must define them with a document container and one (or more, nested or not) setting wrapper.
    """
    tenant = fields.ReferenceField("Tenant", required=True, unique=True)
    core = fields.EmbeddedDocumentField("CoreSettings", required=True, default=lambda: CoreSettings())
    invoicing = fields.EmbeddedDocumentField("InvoicingSettings", required=True, default=lambda: InvoicingSettings())

    meta = {
        "indexes": ["tenant"]
    }

    def __unicode__(self):
        return self.tenant.name


"""
SIGNALS
"""

signals.pre_save.connect(VosaeInvoicingMixin.pre_save, sender=TenantSettings)
