import os

if 'PRODUCTION' in os.environ:
    try:
        from .prod import *
    except ImportError:
        pass

elif 'TRAVIS' in os.environ:
    try:
        from .travis import *
    except ImportError:
        pass

else:
    try:
        from .dev import *
    except ImportError as e:
        print e
