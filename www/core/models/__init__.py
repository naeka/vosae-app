# -*- coding:Utf-8 -*-

from mongoengine import signals

from core.models import embedded
from core.models.embedded import *

from core.models import tenant
from core.models.tenant import *
from core.models import vosae_file
from core.models.vosae_file import *
from core.models import vosae_group
from core.models.vosae_group import *
from core.models import vosae_user
from core.models.vosae_user import *


__all__ = (
    embedded.__all__ +
    tenant.__all__ +
    vosae_file.__all__ +
    vosae_group.__all__ +
    vosae_user.__all__
)


"""
SIGNALS
"""

signals.post_init.connect(Tenant.post_init, sender=Tenant)
signals.pre_save.connect(Tenant.pre_save, sender=Tenant)
signals.pre_save_post_validation.connect(Tenant.pre_save_post_validation, sender=Tenant)
signals.post_save.connect(Tenant.post_save, sender=Tenant)

signals.pre_save.connect(VosaeGroup.pre_save, sender=VosaeGroup)
signals.post_save.connect(VosaeGroup.post_save, sender=VosaeGroup)
signals.post_delete.connect(VosaeGroup.post_delete, sender=VosaeGroup)

signals.pre_save.connect(VosaeUser.pre_save, sender=VosaeUser)
signals.pre_save_post_validation.connect(VosaeUser.pre_save_post_validation, sender=VosaeUser)
signals.post_save.connect(VosaeUser.post_save, sender=VosaeUser)
signals.post_delete.connect(VosaeUser.post_delete, sender=VosaeUser)

signals.pre_save.connect(VosaeFile.pre_save, sender=VosaeFile)
signals.pre_delete.connect(VosaeFile.pre_delete, sender=VosaeFile)
