from collections import defaultdict
from functools import wraps


def update_context_fields(fields=None):
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
