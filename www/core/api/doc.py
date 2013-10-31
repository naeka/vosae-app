# -*- coding:Utf-8 -*-

HELP_TEXT = {
    'tenant': {
        'slug': 'Slug of the organization (max length = 64)',
        'name': 'Name of the organization (max length = 128)',
        'email': 'Email of the organization (max_length = 256)',
        'phone': 'Phone of the organization (max length = 16)',
        'fax': 'Fax of the organization (max length = 16)',
        'registration_info': 'Registration infos of the organization.\nRegistration infos are polymorphic and based upon the registration country of the organization',
        'postal_address': 'Postal/delivery address of the organization',
        'billing_address': 'Billing address of the organization',
        'svg_logo': 'Organization\'s logo based on the open SVG vector format.\nSVG format is preferable since it is better suited to various screen definitions and fits better in vector documents such as PDF',
        'img_logo': 'Organization\'s logo as a regular bitmap format.\nIf an SVG logo is provided, a quality raster equivalent is automatically processed',
        'terms': 'Your terms and conditions. We recommand the use of the common used PDF format',
        'report_settings': 'Vosae allows some customization for your reports. Different settings can be set here',
    },
    'registration_info': {
        'business_entity': 'Business entity (Inc., Ltd., SARL, GmbH, ...)',
        'share_capital': 'Share capital, as a string, must precise the currency',
        'vat_number': 'European Union VAT number',
        'siret': 'French SIRET',
        'rcs_number': 'French RCS number',
    },
    'report_settings': {
        'font_name': 'Name of the font to use on Vosae\'s reports.\nCommon fonts can be used, such as "Helvetica", "Times Roman", etc.\nWill default to Vosae\'s font, Bariol.\nIf the provided font is not supported, we fallback to the closest one',
        'font_size': 'Base font size on reports.\nNote that all sizes (from titles to subnotes) depends on this',
        'base_color': 'The principal color used on the report',
        'force_bw': 'Force all reports to be in grayscale',
        'language': 'Default language for reports',
    },
    'vosae_user_settings': {
        'language_code': 'Language used by the user.\nBy default, Vosae detects the browser\'s language and this settings allows to override this behavior',
        'gravatar_email': 'The email used to have a gravatar associed to the user',
        'email_signature': 'User signature for all emails sent via Vosae',
    },
    'vosae_user': {
        'groups': 'List of the user\'s groups',
        'settings': 'User\'s personal settings',
        'full_name': 'User\'s full name',
        'status': 'User\'s status. One of ["ACTIVE", "DISABLED"]',
        'photo_uri': 'User\'s photo URI',
        'email': 'User\'s email address',
        'specific_permissions': 'A dictionnary of user\'s specific permissions: groups permissions are applied and these ones allow fine-grained perms per user',
        'permissions': 'A dictionnary of user\'s full list of permissions',
    },
    'vosae_group': {
        'name': 'Name of the group (max_length = 64)',
        'created_by': 'Group\'s creator',
        'created_at': 'Group\'s creation datetime',
        'permissions': 'A list group\'s permissions',
    },
    'vosae_file': {
        'issuer': 'The user who have uploaded or generated the file',
        'download_link': 'A private link to download the file (current user must be identified)',
        'stream_link': 'A private link to get the file streamed.\nMainly used to display images (current user must be identified)',
        'name': 'Filename',
        'size': 'Size of the file (in bytes)',
        'sha1_checksum': 'SHA-1 checksum of the file',
        'ttl': 'File\'s hosting duration (in minutes).\nMust be between 1 minute and 5 years.\nTTL is processed each time the file is updated',
        'created_at': 'File\'s creation datetime',
        'modified_at': 'File\'s last modification datetime',
    },
    'zombie_mixin': {
        'status': 'The current status of the resource.\nDepending on the resource type, it can be "ACTIVE", "DELETED", "DISABLED", [...].\nOnly included on detail requests'
    }
}
