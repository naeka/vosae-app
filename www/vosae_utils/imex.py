# -*- coding:Utf-8 -*-


__all__ = (
    'IMEXSerializer',
    'ImportResult'
)


class IMEXSerializer(object):

    """
    (De)Serialize base class for import/export modules

    Each serializer must implement at least one of the following methods:  
        - `serialize(self, **kwargs)`  
        - `deserialize(self, **kwargs)`
    """
    type_name = None
    type_slug = None
    type_mime = None
    type_ext = None


class ImportResult(object):

    def __init__(self):
        self.success = []
        self.errors = []

    @property
    def meta(self):
        succeeded = len(self.success)
        failed = len(self.errors)
        return {
            'total_success': succeeded,
            'total_errors': failed,
            'total_count': succeeded + failed
        }
