# -*- coding: utf-8 -*-

from blinker import Namespace

__all__ = [
    'resource_access',
    'pre_save',
    'pre_save_post_validation',
    'post_save',
    'pre_create',
    'post_create',
    'pre_update',
    'post_update',
    'pre_delete',
    'post_delete',
]


_signals = Namespace()


resource_access = _signals.signal('resource_access')
pre_save = _signals.signal('pre_save')
pre_save_post_validation = _signals.signal('pre_save_post_validation')
post_save = _signals.signal('post_save')
pre_create = _signals.signal('pre_create')
post_create = _signals.signal('post_create')
pre_update = _signals.signal('pre_update')
post_update = _signals.signal('post_update')
pre_delete = _signals.signal('pre_delete')
post_delete = _signals.signal('post_delete')