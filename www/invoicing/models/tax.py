# -*- coding:Utf-8 -*-

from mongoengine import Document, fields

from core.mixins import RestorableMixin
from invoicing.exceptions import InvalidTaxRate


__all__ = ('Tax',)


class Tax(RestorableMixin, Document):
    """A tax is associated to :class:`~invoicing.models.Item`\ s and :class:`~invoicing.models.InvoiceItem`\ s."""
    tenant = fields.ReferenceField("Tenant", required=True)
    name = fields.StringField(required=True, max_length=64)
    rate = fields.DecimalField(required=True, precision=4)

    meta = {
        "indexes": ["tenant", "name"],

        # Vosae specific
        "vosae_permissions": ("change_invoicingsettings",),
        "vosae_mandatory_permissions": ("invoicing_access",),
    }

    def __unicode__(self):
        return u'%s (%s%%)' % (self.name, self.rate * 100)

    def save(self, *args, **kwargs):
        """
        The :class:`~invoicing.models.Tax` rate should not be updated.

        If needed, the tax must be removed and then re-added with the updated rate value.
        """
        if hasattr(self, '_changed_fields') and 'rate' in self._changed_fields:
            raise InvalidTaxRate("Tax rate is not modifiable.")
        super(Tax, self).save(*args, **kwargs)
