# -*- coding:Utf-8 -*-

from django.utils.translation import pgettext_lazy
from mongoengine import EmbeddedDocument, fields


__all__ = (
    'Address',
)


class Address(EmbeddedDocument):

    """An address wrapper which can be embedded in any object."""
    TYPES = (
        ("HOME", pgettext_lazy("address type", "Home")),
        ("WORK", pgettext_lazy("address type", "Work")),
        ("DELIVERY", pgettext_lazy("address type", "Delivery")),
        ("BILLING", pgettext_lazy("address type", "Billing")),
        ("OTHER", pgettext_lazy("address type", "Other"))
    )

    label = fields.StringField(max_length=64)
    type = fields.StringField(choices=TYPES)
    postoffice_box = fields.StringField(max_length=64)
    street_address = fields.StringField(required=True, max_length=128)
    extended_address = fields.StringField(max_length=128)
    postal_code = fields.StringField(max_length=16)
    city = fields.StringField(max_length=64)
    state = fields.StringField(max_length=64)
    country = fields.StringField(max_length=64)
    geo_point = fields.GeoPointField()

    def __eq__(self, other):
        """Equal comparison should only be based on fields values"""
        if isinstance(other, Address) and \
           self.label == other.label and \
           self.type == other.type and \
           self.postoffice_box == other.postoffice_box and \
           self.street_address == other.street_address and \
           self.extended_address == other.extended_address and \
           self.postal_code == other.postal_code and \
           self.city == other.city and \
           self.state == other.state and \
           self.country == other.country and \
           self.geo_point == other.geo_point:
            return True
        else:
            return False

    @staticmethod
    def concat_fields(field1, field2):
        """
        Method used in the :func:`~contacts.models.Address.get_formatted` method
        to concatenate fields like state and country.
        """
        if not field1 and not field2:
            return None
        if field1 and not field2:
            return field1
        if not field1 and field2:
            return field2
        if field1 and field2:
            return ", ".join([field1, field2])

    def get_formatted(self):
        """
        Returns a concatenated list of :class:`~contacts.models.Address` attributes:

        - Street address
        - Extended address, post office box
        - Postal code, City
        - State, Country
        """
        ret = [
            self.street_address,
            Address.concat_fields(self.extended_address, self.postoffice_box),
            Address.concat_fields(self.postal_code, self.city),
            Address.concat_fields(self.state, self.country)
        ]
        # Returns only non-blank lines
        return [line for line in ret if line]
