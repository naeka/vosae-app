# -*- coding:Utf-8 -*-

from collections import OrderedDict
from dateutil.parser import parse
from mongoengine import *
from vobject.base import toVName
from django.utils.translation import ugettext as _
import vobject
import csv
try:
    import cStringIO
    StringIO = cStringIO
except ImportError:
    import StringIO

from vosae_utils import IMEXSerializer, ImportResult
from models import Contact, Organization, Email, Phone, Address


__all__ = [
    'EXPORTABLE_DOCUMENTS_TYPES',
    'get_exportable_documents',
    'VCardSerializer',
    'CSVSerializer'
]


EXPORTABLE_DOCUMENTS_TYPES = (
    'CONTACT',
    'ORGANIZATION'
)


def get_exportable_documents(export):
    documents = []
    if 'CONTACT' in export.documents_types:
        qs = Contact.objects.filter(tenant=export.tenant, state='ACTIVE')
        serializer = CSVSerializer()
        documents.append((
            [serializer.serialize(qs)],
            lambda buf: '{0}/{1}.csv'.format(_('Contacts'), _('Contacts')),
            lambda buf: buf
        ))
    if 'ORGANIZATION' in export.documents_types:
        qs = Organization.objects.filter(tenant=export.tenant, state='ACTIVE')
        serializer = CSVSerializer()
        documents.append((
            [serializer.serialize(qs)],
            lambda buf: '{0}/{1}.csv'.format(_('Contacts'), _('Organizations')),
            lambda buf: buf
        ))
    return documents


class VCardSerializer(IMEXSerializer):

    """vCard serializer"""
    type_name = 'vCard'
    type_slug = 'vcard'
    type_mime = ('text/vcard', 'text/x-vcard')
    type_ext = 'vcf'

    def serialize(self, contacts):
        return ''.join(self._vcard_string(contact) for contact in contacts)

    def deserialize(self, import_buffer, target_class, tenant):
        result = ImportResult()
        EMAIL_TYPES = tuple(t[0] for t in Email.TYPES)
        PHONE_TYPES = tuple(t[0] for t in Phone.TYPES)
        PHONE_SUBTYPES = tuple(t[0] for t in Phone.SUBTYPES)
        ADDRESS_TYPES = tuple(t[0] for t in Address.TYPES)
        for vcard in vobject.readComponents(import_buffer):
            if issubclass(vcard.behavior, vobject.vcard.VCard3_0):
                contact = target_class(tenant=tenant)
                try:
                    if isinstance(contact, Contact):
                        assert vcard.getChildValue('n').family
                        assert vcard.getChildValue('n').given
                        contact.name = vcard.getChildValue('n').family
                        contact.firstname = vcard.getChildValue('n').given
                        contact.additional_names = vcard.getChildValue('n').additional or None
                        # Handle organizations ?
                        if vcard.getChildValue('bday'):
                            contact.birthday = parse(vcard.bday.value)
                    if isinstance(contact, Organization):
                        assert vcard.getChildValue('org')
                        contact.corporate_name = vcard.getChildValue('org')

                    emails = vcard.contents.get(toVName('email')) or []
                    for email in emails:
                        email_type = None
                        try:
                            email_type = email.type_param
                        except:
                            pass
                        contact.emails.append(Email(
                            type=email_type if email_type in EMAIL_TYPES else None,
                            email=email.value
                        ))

                    phones = vcard.contents.get(toVName('tel')) or []
                    for phone in phones:
                        phone_types = []
                        phone_type = None
                        phone_subtype = None
                        try:
                            phone_types = phone.type_paramlist
                            for ptype in phone_types:
                                if ptype in PHONE_TYPES and not phone_type:
                                    phone_type = ptype
                                elif ptype in PHONE_SUBTYPES and not phone_subtype:
                                    phone_subtype = ptype
                        except:
                            pass
                        contact.phones.append(Phone(
                            type=phone_type,
                            subtype=phone_subtype,
                            phone=phone.value
                        ))

                    addresses = vcard.contents.get(toVName('adr')) or []
                    for address in addresses:
                        address_type = None
                        try:
                            address_type = address.type_param
                        except:
                            pass
                        contact.addresses.append(Address(
                            type=address_type if address_type in ADDRESS_TYPES else None,
                            postoffice_box=address.value.box,
                            street_address=address.value.street,
                            extended_address=address.value.extended,
                            postal_code=address.value.code,
                            city=address.value.city,
                            state=address.value.region,
                            country=address.value.country
                        ))
                    contact.save()
                    result.success.append(contact)
                except:
                    record_name = vcard.getChildValue('fn')
                    if not record_name:
                        name = vcard.getChildValue('n').family
                        firstname = vcard.getChildValue('n').given
                        if name and firstname:
                            record_name = u'%s %s' % (firstname, name)
                        elif name:
                            record_name = name
                        elif firstname:
                            record_name = firstname
                    if not record_name:
                        try:
                            record_name = vcard.getChildValue('org')[0]
                        except:
                            pass
                    if not record_name:
                        record_name = _('No name')
                    result.errors.append(record_name)
        return result

    def _vcard_string(self, contact):
        """Returns a string containing serialized vCard data."""
        v = vobject.vCard()

        if isinstance(contact, Contact):
            v.add('n').value = vobject.vcard.Name(family=contact.name, given=contact.firstname)
            v.add('fn').value = contact.get_full_name()
            if contact.organization:
                v.add('org').value = [contact.organization.corporate_name]
            if contact.birthday:
                v.add('bday').value = contact.birthday.isoformat()

        elif isinstance(contact, Organization):
            v.add('n').value = vobject.vcard.Name()
            v.add('fn').value = ''
            v.add('org').value = [contact.corporate_name]

        # XXX: Add PHOTO

        for email in contact.emails:
            e = v.add('email')
            e.value = email.email
            if email.type:
                e.type_param = email.type

        for phone in contact.phones:
            types = []
            if phone.type:
                types.append(phone.type)
            if phone.subtype:
                types.append(phone.subtype)
            p = v.add('tel')
            if types:
                p.type_paramlist = types
            p.value = phone.phone

        for address in contact.addresses:
            a = v.add('adr')
            if address.type:
                a.type_param = address.type
            a.value = vobject.vcard.Address(
                street=address.street_address or '',
                city=address.city or '',
                region=address.state or '',
                code=address.postal_code or '',
                country=address.country or '',
                box=address.postoffice_box or '',
                extended=address.extended_address or ''
            )

        return v.serialize()


class CSVSerializer(IMEXSerializer):

    """CSV serializer"""
    type_name = 'CSV'
    type_slug = 'csv'
    type_mime = ('text/csv',)
    type_ext = 'csv'
    fields = (
        ("id", ''), ("First Name", ''), ("Middle Name", ''), ("Last Name", ''), ("Title", ''),
        ("Suffix", ''), ("Initials", ''), ("Web Page", ''), ("Gender", ''),
        ("Birthday", ''), ("Anniversary", ''), ("Location", ''), ("Language", ''),
        ("Internet Free Busy", ''), ("Notes", ''), ("E-mail Address", ''),
        ("E-mail 2 Address", ''), ("E-mail 3 Address", ''), ("Primary Phone", ''),
        ("Home Phone", ''), ("Home Phone 2", ''), ("Mobile Phone", ''), ("Pager", ''),
        ("Home Fax", ''), ("Home Address", ''), ("Home Street", ''), ("Home Street 2", ''),
        ("Home Street 3", ''), ("Home Address PO Box", ''), ("Home City", ''),
        ("Home State", ''), ("Home Postal Code", ''), ("Home Country", ''),
        ("Spouse", ''), ("Children", ''), ("Manager's Name", ''), ("Assistant's Name", ''),
        ("Referred By", ''), ("Company Main Phone", ''), ("Business Phone", ''),
        ("Business Phone 2", ''), ("Business Fax", ''), ("Assistant's Phone", ''),
        ("Company", ''), ("Job Title", ''), ("Department", ''), ("Office Location", ''),
        ("Organizational ID Number", ''), ("Profession", ''), ("Account", ''),
        ("Business Address", ''), ("Business Street", ''), ("Business Street 2", ''),
        ("Business Street 3", ''), ("Business Address PO Box", ''), ("Business City", ''),
        ("Business State", ''), ("Business Postal Code", ''), ("Business Country", ''),
        ("Other Phone", ''), ("Other Fax", ''), ("Other Address", ''), ("Other Street", ''),
        ("Other Street 2", ''), ("Other Street 3", ''), ("Other Address PO Box", ''),
        ("Other City", ''), ("Other State", ''), ("Other Postal Code", ''),
        ("Other Country", ''), ("Callback", ''), ("Car Phone", ''), ("ISDN", ''),
        ("Radio Phone", ''), ("TTY/TDD Phone", ''), ("Telex", ''), ("User 1", ''),
        ("User 2", ''), ("User 3", ''), ("User 4", ''), ("Keywords", ''), ("Mileage", ''),
        ("Hobby", ''), ("Billing Information", ''), ("Directory Server", ''),
        ("Sensitivity", ''), ("Priority", ''), ("Private", ''), ("Categories", '')
    )

    def serialize(self, contacts):
        self.csv_buffer = StringIO.StringIO()
        self.writer = csv.writer(self.csv_buffer)
        self.writer.writerow([k for k, v in self.fields])
        for contact in contacts:
            self._append_csv_row(contact)
        return self.csv_buffer.getvalue()

    def _append_csv_row(self, contact):
        """Append a serialized CSV row to buffer."""
        row_data = OrderedDict(self.fields)
        row_data["id"] = unicode(contact.id)
        if isinstance(contact, Contact):
            row_data["First Name"] = contact.firstname or ''
            row_data["Last Name"] = contact.name or ''
            if contact.organization:
                row_data["Company"] = contact.organization.corporate_name or ''
            if contact.birthday:
                row_data["Birthday"] = contact.birthday.isoformat() or ''

        elif isinstance(contact, Organization):
            row_data["Company"] = contact.corporate_name or ''

        for idx, email in enumerate(contact.emails[:3], 1):
            if idx == 1:
                key = "E-mail Address"
            else:
                key = "E-mail %d Address" % idx
            row_data[key] = email.email or ''

        for phone in contact.phones:
            if phone.type == 'HOME':
                if phone.subtype == 'CELL':
                    if not row_data["Mobile Phone"]:
                        row_data["Mobile Phone"] = phone.phone
                    else:
                        row_data["Other Phone"] = phone.phone
                elif phone.subtype == 'FAX':
                    if not row_data["Home Fax"]:
                        row_data["Home Fax"] = phone.phone
                    else:
                        row_data["Other Fax"] = phone.phone
                else:
                    if not row_data["Home Phone"]:
                        row_data["Home Phone"] = phone.phone
                    elif not row_data["Home Phone 2"]:
                        row_data["Home Phone 2"] = phone.phone
                    elif not row_data["Other Phone"]:
                        row_data["Other Phone"] = phone.phone
                    else:
                        continue
            elif phone.type == 'WORK':
                if phone.subtype == 'CELL':
                    if not row_data["Mobile Phone"]:
                        row_data["Mobile Phone"] = phone.phone
                    elif not row_data["Business Phone"]:
                        row_data["Business Phone"] = phone.phone
                    elif not row_data["Other Phone"]:
                        row_data["Other Phone"] = phone.phone
                    else:
                        continue
                elif phone.subtype == 'FAX':
                    if not row_data["Business Fax"]:
                        row_data["Business Fax"] = phone.phone
                    elif not row_data["Other Fax"]:
                        row_data["Other Fax"] = phone.phone
                    else:
                        continue
                else:
                    if not row_data["Business Phone"]:
                        row_data["Business Phone"] = phone.phone
                    elif not row_data["Business Phone 2"]:
                        row_data["Business Phone 2"] = phone.phone
                    elif not row_data["Other Phone"]:
                        row_data["Other Phone"] = phone.phone
                    else:
                        continue
            else:
                continue

        for address in contact.addresses:
            if address.type == 'HOME':
                if row_data["Home Address"]:
                    continue  # Only one possible address
                row_data["Home Address"] = '\r\n'.join(address.get_formatted())
                row_data["Home Street"] = address.street_address or ''
                row_data["Home Street 2"] = address.extended_address or ''
                row_data["Home Address PO Box"] = address.postoffice_box or ''
                row_data["Home City"] = address.city or ''
                row_data["Home State"] = address.state or ''
                row_data["Home Postal Code"] = address.postal_code or ''
                row_data["Home Country"] = address.country or ''
            elif address.type == 'WORK':
                if row_data["Business Address"]:
                    continue  # Only one possible address
                row_data["Business Address"] = '\r\n'.join(address.get_formatted())
                row_data["Business Street"] = address.street_address or ''
                row_data["Business Street 2"] = address.extended_address or ''
                row_data["Business Address PO Box"] = address.postoffice_box or ''
                row_data["Business City"] = address.city or ''
                row_data["Business State"] = address.state or ''
                row_data["Business Postal Code"] = address.postal_code or ''
                row_data["Business Country"] = address.country or ''

        self.writer.writerow([s.encode('utf-8') for s in row_data.values()])
