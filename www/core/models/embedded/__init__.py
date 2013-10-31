# -*- coding:Utf-8 -*-

from core.models.embedded import registration_info
from core.models.embedded.registration_info import *
from core.models.embedded import report_settings
from core.models.embedded.report_settings import *
from core.models.embedded import vosae_permissions
from core.models.embedded.vosae_permissions import *
from core.models.embedded import vosae_user_settings
from core.models.embedded.vosae_user_settings import *


__all__ = (
    registration_info.__all__ +
    report_settings.__all__ +
    vosae_permissions.__all__ +
    vosae_user_settings.__all__
)
