import logging
import traceback
from django.shortcuts import render, redirect
from main.middleware.exception.exceptions import (
    RuntimeException,
    BondAreaNameException
)

logger = logging.getLogger(__name__)


class ExceptionHandleMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        self.__write_logging(request, exception)
        if isinstance(exception, RuntimeException):
            request.context["lblMsg"] = exception.get_message()
        elif isinstance(exception, BondAreaNameException):
            request.context["lblMsg"] = str(exception).replace("(0)", request.path[1:-1])
            return render(request, "home.html", request.context)
        else:
            request.context["lblMsg"] = f"Server error: {str(exception)}"
        url_name = request.resolver_match.url_name
        return render(request, f"{url_name}.html", request.context)

    def __write_logging(self, request, exception):
        logger.error((
            'HttpRequest [method={}, content_type={}, url={}], '
            'error={}, '
            'backtrace={}'
        ).format(
            request.method,
            request.content_type,
            request.path,
            str(exception).replace("(0)", request.path[1:-1]),
            traceback.format_exc(),
        ))
