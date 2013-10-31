import os

if 'HEROKU' in os.environ:
    from johnny.cache import enable
    enable()
