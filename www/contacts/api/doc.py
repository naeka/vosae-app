# -*- coding:Utf-8 -*-

HELP_TEXT = {
    'entity': {
        'id': 'Vosae identifier',
        'photo_source': 'Source of the photo. If not provided, a default photo will be used',
        'photo': 'If photo_source is LOCAL, use this file as photo.\nPhoto URI should always be used for display',
        'gravatar_mail': 'Contact\'s email used for displaying gravatar pictures',
        'addresses': 'Contact\'s addresses list',
        'emails': 'Contact\'s email address (max length = 128)',
        'phones': 'Contact\'s phone (max length = 16)',
        'note': 'A note for a contact (max length = 2048)',
        'photo_uri': 'Contact\'s photo URI',
        'creator': 'Contacts\'s creator',
    },
    'contact': {
        'name': 'Contact\'s name (max_length = 64)',
        'firstname': 'Contact\'s first name (max_length = 64)',
        'additional_names': 'Contact\'s additional names (max_length = 128)',
        'civility': 'Contact\'s civility',
        'birthday': 'Contact\'s birthday (ie. 01/01/1970)',
        'organization': 'Organization related to the contact',
        'role': 'Contacts\'s role inside his organization',
    },
    'organization': {
        'corporate_name': 'Organization\'s name',
        'tags': 'List of the organization\'s tags',
        'contacts': 'List of the organization\'s contacts',
    },
    'address': {
        'label': 'Address label (max_length = 64)',
        'type': 'The address type.\nOne of: <ul><li class="text-info">HOME</li> <li class="text-info">WORK</li> <li class="text-info">DELIVERY</li> <li class="text-info">BILLING</li> <li class="text-info">OTHER</li></ul>',
        'postoffice_box': 'The postoffice box (max_length = 64)',
        'street_address': 'The main address (max_length = 128)',
        'extended_address': 'A complementary address (ie. building, level; max_length = 128)',
        'postal_code': 'The postal code (max_length = 16)',
        'city': 'The city (max_length = 64)',
        'state': 'The state (max_length = 64)',
        'country': 'The country (max_length = 64)'
    },
    'email': {
        'label': 'Email label (max_length = 64)',
        'type': 'The email type.\nOne of: <ul><li class="text-info">HOME</li> <li class="text-info">WORK</li></ul>',
        'email': 'The email (max_length = 128)'
    },
    'phone': {
        'label': 'Phone label (max_length = 64)',
        'type': 'The phone type.\nOne of: <ul><li class="text-info">HOME</li> <li class="text-info">WORK</li></ul>',
        'subtype': 'The Phone sub type.\nOne of: <ul><li class="text-info">CELL</li> <li class="text-info">FAX</li></ul>',
        'phone': 'The phone number (max_length = 16)'
    }
}
