# -*- coding:Utf-8 -*-

from django.conf import settings
from django.utils import translation
from contextlib import contextmanager
from functools import wraps

import hashlib
import random
import re


__all__ = (
    'StateList',
    'generate_sha1',
    'get_reserved_urlroot',
    'respect_language',
    'respects_language'
)


class StateList(tuple):

    """Used to handle states without direct string comparison. Avoids unicode conficts."""

    def __getattr__(self, name):
        try:
            return super(StateList, self).__getattr__(name)
        except AttributeError as error:
            for k, v in self:
                if k == name:
                    return k
            raise error


def generate_sha1(string, salt=None):
    """
    Generates a sha1 hash for supplied string. Doesn't need to be very secure
    because it's not used for password checking. We got Django for that.

    :param string:
        The string that needs to be encrypted.

    :param salt:
        Optionally define your own salt. If none is supplied, will use a random
        string of 5 characters.

    :return: Tuple containing the salt and hash.

    """
    if not salt:
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    hash = hashlib.sha1(salt + str(string)).hexdigest()

    return (salt, hash)


def get_reserved_urlroot(urllist):
    root_urls = [language[0] for language in settings.LANGUAGES]
    for entry in urllist:
        if re.match('^\^[\w]', entry.regex.pattern, flags=re.IGNORECASE):
            match = re.sub(r'\\(.)', r'\1', entry.regex.pattern)[1:-1]
            rpos = match.find('/')
            if rpos > 0:
                match = match[:rpos]
            if match not in root_urls:
                root_urls.append(match)
        if entry.regex.pattern is '' and hasattr(entry, 'url_patterns'):
            for match in get_reserved_urlroot(entry.url_patterns):
                if match not in root_urls:
                    root_urls.append(match)
    return root_urls


@contextmanager
def respect_language(language):
    """Context manager that changes the current translation language for
    all code inside the following block.

    Can e.g. be used inside tasks like this::

        from celery import task
        from djcelery.common import respect_language

        @task
        def my_task(language=None):
            with respect_language(language):
                pass
    """
    if language:
        prev = translation.get_language()
        translation.activate(language)
        try:
            yield
        finally:
            translation.activate(prev)
    else:
        yield


def respects_language(fun):
    """Decorator for tasks with respect to site's current language.
    You can use this decorator on your tasks together with default @task
    decorator (remember that the task decorator must be applied last).

    See also the with-statement alternative :func:`respect_language`.

    **Example**:

    .. code-block:: python

        @task
        @respects_language
        def my_task()
            # localize something.

    The task will then accept a ``language`` argument that will be
    used to set the language in the task, and the task can thus be
    called like:

    .. code-block:: python

        from django.utils import translation
        from myapp.tasks import my_task

        # Pass the current language on to the task
        my_task.delay(language=translation.get_language())

        # or set the language explicitly
        my_task.delay(language='no.no')

    """
    @wraps(fun)
    def _inner(*args, **kwargs):
        with respect_language(kwargs.pop('language', None)):
            return fun(*args, **kwargs)
    return _inner
