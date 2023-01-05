import logging
import traceback
from django.shortcuts import render
from main.middleware.exception.exceptions import RuntimeException
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)


class ExceptionHandleMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, RuntimeException):
            request.context["lblMsg"] = exception.get_message()
        else:
            request.context["lblMsg"] = f"Server error: {str(exception)}"
        self.__write_logging(request, exception)
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
            str(exception),
            traceback.format_exc(),
        ))
