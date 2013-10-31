====
Core
====



Embedded resources
==================


VosaeUserSettings
-----------------

.. autoclass:: core.models.embedded.VosaeUserSettings
   :members:

.. autoclass:: core.api.resources.embedded.VosaeUserSettingsResource
   :members:


VosaePermissions
----------------

.. autoclass:: core.models.embedded.VosaePermissions
   :members:


ReportSettings
--------------

.. autoclass:: core.models.embedded.ReportSettings
   :members:

.. autoclass:: core.api.resources.embedded.ReportSettingsResource
   :members:


RegistrationInfo
----------------

.. autoclass:: core.models.embedded.RegistrationInfo
   :members:

.. autoclass:: core.api.resources.embedded.RegistrationInfoResource
   :members:


Localized RegistrationInfo
''''''''''''''''''''''''''

.. autoclass:: core.models.embedded.BERegistrationInfo
    :members:

.. autoclass:: core.api.resources.embedded.BERegistrationInfoResource
    :members:

------

.. autoclass:: core.models.embedded.CHRegistrationInfo
    :members:

.. autoclass:: core.api.resources.embedded.CHRegistrationInfoResource
    :members:

------

.. autoclass:: core.models.embedded.FRRegistrationInfo
    :members:

.. autoclass:: core.api.resources.embedded.FRRegistrationInfoResource
    :members:

------

.. autoclass:: core.models.embedded.GBRegistrationInfo
    :members:

.. autoclass:: core.api.resources.embedded.GBRegistrationInfoResource
    :members:

------

.. autoclass:: core.models.embedded.LURegistrationInfo
    :members:

.. autoclass:: core.api.resources.embedded.LURegistrationInfoResource
    :members:

------

.. autoclass:: core.models.embedded.USRegistrationInfo
    :members:

.. autoclass:: core.api.resources.embedded.USRegistrationInfoResource
    :members:

------

.. autoclass:: core.models.embedded.BERegistrationInfo
    :members:

.. autoclass:: core.api.resources.embedded.BERegistrationInfoResource
    :members:



Main resources
==============


VosaeCustomer
-------------

.. autoclass:: core.models.VosaeCustomer
   :members:

.. autoclass:: core.api.resources.VosaeCustomerResource
   :members:


VosaeGroup
----------

.. autoclass:: core.models.VosaeGroup
   :members:

.. autoclass:: core.api.resources.VosaeGroupResource
   :members:


VosaeUser
---------

.. autoclass:: core.models.VosaeUser
   :members:

.. autoclass:: core.api.resources.VosaeUserResource
   :members:


VosaeFile
---------

.. autoclass:: core.models.VosaeFile
   :members:

.. autoclass:: core.api.resources.VosaeFileResource
   :members:



API utilities
=============


Authentication
--------------

.. autoclass:: core.api.utils.VosaeSessionAuthentication
   :members:

.. autoclass:: core.api.utils.VosaeApiKeyAuthentication
   :members:


Authorization
-------------

.. autoclass:: core.api.utils.VosaeGenericAuthorization
   :members:

.. autoclass:: core.api.utils.VosaeUserAuthorization
   :members:


Mixins
------

.. autoclass:: core.api.utils.MultipartMixinResource
   :members:

.. autoclass:: core.api.utils.VosaeIMEXMixinResource
   :members:

.. autoclass:: core.api.utils.ZombieMixinResource
   :members:

.. autoclass:: core.api.utils.WakeUpMixinResource
   :members:

.. autoclass:: core.api.utils.RemoveFilesOnReplaceMixinResource
   :members:


Resources
---------

.. autoclass:: core.api.utils.VosaeResource
   :members:

.. autoclass:: core.api.utils.VosaeTenantResource
   :members:


Throttling
----------

.. autoclass:: core.api.utils.VosaeCacheThrottle
   :members:

.. autoclass:: core.api.utils.VosaeCacheDBThrottle
   :members:'