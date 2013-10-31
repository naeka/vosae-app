# -*- coding:Utf-8 -*-

from core.api.resources import embedded
from core.api.resources.embedded import *

from core.api.resources import tenant
from core.api.resources.tenant import *
from core.api.resources import vosae_group
from core.api.resources.vosae_group import *
from core.api.resources import vosae_user
from core.api.resources.vosae_user import *
from core.api.resources import vosae_file
from core.api.resources.vosae_file import *
from core.api.resources import vosae_search
from core.api.resources.vosae_search import *


__all__ = (
    embedded.__all__ +
    tenant.__all__ +
    vosae_group.__all__ +
    vosae_user.__all__ +
    vosae_file.__all__ +
    vosae_search.__all__
)
