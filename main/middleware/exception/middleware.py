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
            self.__write_logging(request, exception)
            request.context["lblMsg"] = exception.get_message()
            return self.__response(request)
        else:
            self.__write_logging(request, exception)
            request.context["lblMsg"] = f"Server error: {str(exception)}"
            return self.__response(request)

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

    def __response(self, request):
        url_name = request.resolver_match.url_name
        if url_name[:3] == "pop":
            return render(request, "popup/popCommon.html", request.context)
        return render(request, f"{url_name}.html", request.context)
