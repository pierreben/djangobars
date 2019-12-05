from importlib import import_module

from django.conf import settings
from django.urls import reverse


def _url(context, url_name, *args, **kwargs):
    return reverse(url_name, args=args, kwargs=kwargs)


_djangobars_ = {
    'helpers': {
        'url': _url
    }
}


extra_helpers = getattr(settings, 'DJANGOBARS_HELPERS', None)

if extra_helpers:
    mod = import_module(extra_helpers)

    public_props = (name for name in dir(mod) if not name.startswith('__') and name.startswith('_'))
    for helper in public_props:
        _djangobars_['helpers'][helper[1:]] = getattr(mod, helper)
