# -*- coding:Utf-8 -*-

from mongoengine import EmbeddedDocument, fields
from decimal import Decimal


__all__ = ('InvoiceItem',)


class InvoiceItem(EmbeddedDocument):

    """
    An :class:`~invoicing.models.InvoiceItem` is an :class:`~invoicing.models.Item` embedded
    in the :class:`~invoicing.models.InvoiceRevision` items list.

    It corresponds to the line of an invoice.
    """
    reference = fields.StringField(required=True, max_length=32)
    description = fields.StringField(required=True, max_length=1024)
    quantity = fields.DecimalField(required=True, default=lambda: Decimal("1"))
    unit_price = fields.DecimalField(required=True)
    tax = fields.ReferenceField("Tax", required=True)
    optional = fields.BooleanField(required=True, default=False)
    item_id = fields.ObjectIdField()
    #footnote = fields.StringField(max_length=512)

    def __unicode__(self):
        if isinstance(self.reference, basestring):
            return self.reference
        return unicode(self.reference)

    @property
    def total_price(self):
        """Return the total price for this item, considering the quantity."""
        return self.quantity * self.unit_price
