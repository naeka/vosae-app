# -*- coding:Utf-8 -*-

HELP_TEXT = {
    'vosae_calendar': {
        'summary': 'The summary (title) of the calendar (max_length = 64)',
        'description': 'The description of the calendar (max_length = 1024)',
        'location': 'The location fo the calendar (max_length = 256)',
        'acl': 'Calendar\'s access control lists',
        'timezone': 'The timezone of the calendar (default = "UTC")',
    },
    'calendar_list': {
        'summary_override': 'Non-owners can set a different summary for shared calendars',
        'color': 'Calendar\'s color',
        'selected': 'A calendar can be shown or not on the organizer.\nIf selected, the calendar is shown by default',
        'calendar': 'The related calendar',
        'is_own': 'Determine if the calendar belongs to the user',
        'reminders': 'Default event reminders for this calendar',
    },
    'vosae_event': {
        'status': 'Status of the event.\nOne of: <ul><li class="text-info">CONFIRMED</li> <li class="text-info">TENTATIVE</li> <li class="text-info">CANCELLED</li></ul>',
        'created_at': 'Event\'s creation datetime',
        'updated_at': 'Event\'s modification datetime',
        'summary': 'Event\'s summary (max_length = 64)',
        'description': 'Event\'s description (max_length = 1024)',
        'location': 'Event\'s location (max_length = 512)',
        'color': 'Event\'s custom color (6-hexadecimal, prefixed by "#")',
        'start': 'Event\'s start date(time)',
        'end': 'Event\'s end date(time)',
        'recurrence': 'Event\'s recurrence rules.\nPlease note that infinite RRULESET are shrinked to the first 730 occurrences',
        'original_start': 'If the event is recurring, this belongs to the original event start date(time)',
        'instance_id': 'If the event is recurring, the occurrence instance id',
        'transparency': 'Event\'s transparency.\nOne of: <ul><li class="text-info">TRANSPARENT</li> <li class="text-info">OPAQUE</li></ul>',
        'calendar': 'Event\'s related calendar',
        'calendar_list': 'Event\'s related calendar list',
        'creator': 'User which have created the event',
        'organizer': 'Event\'s organizer.\nCan be different of the creator',
        'attendees': 'Event\'s attendees.\nCan be internal Vosae users or external attendees identified by their name/email',
        'reminders': 'Event\'s custom reminders',
    },
    'attendee': {
        'email': 'E-mail of the attendee',
        'display_name': 'Name of the attendee, usually first and last name (max_length = 128)',
        'organizer': 'Indicates if this attendee is the event\'s organizer',
        'vosae_user': 'Related Vosae user, if exists',
        'optional': 'Indicates if the attendee venue is optional',
        'response_status': 'Attendee\'s response status.\nOne of: <ul><li class="text-info">NEEDS-ACTION (default)</li> <li class="text-info">DECLINED</li> <li class="text-info">TENTATIVE</li> <li class="text-info">ACCEPTED</li></ul>',
        'comment': 'A comment made by the attendee (max_length = 1024)',
        'photo_uri': 'User photo URI',
    },
    'calendar_acl': {
        'rules': 'List of access rules',
        'role': 'Role (access type) of the principal.\nOne of: <ul><li class="text-info">NONE (to revoke access, when granted by a group)</li> <li class="text-info">READER</li> <li class="text-info">WRITER</li> <li class="text-info">OWNER</li></ul>',
        'principal': 'The principal of the ACL. Can be either a group or a user'
    },
    'event_date_time': {
        'date': 'Exact date',
        'datetime': 'Exact datetime',
        'timezone': 'Timezone used. This have no effect with the date field',
    },
    'reminder': {
        'method': 'Method used for the reminder.\nOne of: <ul><li class="text-info">EMAIL</li><li class="text-info">POPUP</li></ul>',
        'minutes': 'Time in minutes before the event\'s start to trigger the reminder (15 days maximum - 21600 minutes)',
        'use_default': 'Use the default reminders defined in the calendar_list',
        'overrides': 'List of reminders which override those defined in the calendar_list',
    }
}
