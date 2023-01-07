from collections import defaultdict
from functools import wraps

from main.common.utils import ConfigIni


def update_context_fields():
    """
    Assign context data to request
    @update_context
    def my_view():
    ....
    """

    def inner_func(f):
        @wraps(f)
        def wrap(request, *args, **kwargs):
            request.context = defaultdict(str)
            if request.method == "POST":
                for field in request.POST:
                    request.context[field] = request.POST.get(field, "")
            return f(request, *args, **kwargs)

        return wrap

    return inner_func


def update_context():
    """
    Assign context data to request
    @update_context
    def my_view():
    ....
    """

    def inner_func(f):
        @wraps(f)
        def wrap(request, *args, **kwargs):
            request.context = defaultdict(str)
            if request.method == "POST":
                for field in request.POST:
                    request.context[field] = request.POST.get(field, "")
                return f(request, *args, **kwargs)
            return f(request, *args, **kwargs)

        return wrap

    return inner_func


def load_cfs_ini(cfs_menu):
    """
    Load Cfs ini
    @load_cfs_ini
    def my_view():
    ....
    """

    def inner_func(f):
        @wraps(f)
        def wrap(request, *args, **kwargs):
            request.cfs_ini = defaultdict(str)
            ini = ConfigIni()
            ini.get_config_ini_info(request, cfs_menu)
            return f(request, *args, **kwargs)

        return wrap

    return inner_func
