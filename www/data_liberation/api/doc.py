# -*- coding:Utf-8 -*-

HELP_TEXT = {
    'export': {
        'created_at': 'Export creation date',
        'language': 'Language used for the export',
        'documents_types': 'Types of documents exported',
        'from_date': 'If the export is based on a date-range, first date boundary',
        'to_date': 'If the export is based on a date-range, last date boundary',
        'issuer': 'The used who requested the export',
        'zipfile': 'Export zip file. Exports are asynchronously generated and zipped.\nThis field is null just after the export creation: when the zip file is fully generated, a mail is sent to the requester and zipfile is present for the upcoming requests',
    },
}
