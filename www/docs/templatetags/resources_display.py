from django import template
import inflection

register = template.Library()


def classname(value, strip_resource=True):
    if not strip_resource:
        return value.__class__.__name__
    else:
        return value.__class__.__name__.replace('Resource', '')


def camelize(value):
    return inflection.camelize(value)


def humanize(value):
    return inflection.humanize(value)


def underscore(value):
    return inflection.underscore(value)


register.filter('classname', classname)
register.filter('camelize', camelize)
register.filter('humanize', humanize)
register.filter('underscore', underscore)
