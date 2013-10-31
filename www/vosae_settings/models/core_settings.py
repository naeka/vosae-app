# -*- coding:Utf-8 -*-

from mongoengine import fields, EmbeddedDocument


"""
CORE SETTINGS
All settings related to the core app.
Mainly global settings
"""


__all__ = (
    'CoreSettings',
)


class StorageQuotasSettings(EmbeddedDocument):

    """Quotas counters"""
    PER_USER_SPACE = 1 * 1024 * 1024 * 1024  # 1 GiB

    allocated_space = fields.IntField(required=True, min_value=0, default=PER_USER_SPACE)
    used_space = fields.IntField(required=True, min_value=0, default=0)


class CoreSettings(EmbeddedDocument):

    """A wrapper to global settings."""
    quotas = fields.EmbeddedDocumentField("StorageQuotasSettings", required=True, default=lambda: StorageQuotasSettings())
