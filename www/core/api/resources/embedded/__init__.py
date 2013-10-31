# -*- coding:Utf-8 -*-

from core.api.resources.embedded import registration_info
from core.api.resources.embedded.registration_info import *
from core.api.resources.embedded import report_settings
from core.api.resources.embedded.report_settings import *
from core.api.resources.embedded import vosae_user_settings
from core.api.resources.embedded.vosae_user_settings import *


__all__ = (
    registration_info.__all__ +
    report_settings.__all__ +
    vosae_user_settings.__all__
)
