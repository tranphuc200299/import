import logging

from django import template

register = template.Library()

_logger = logging.getLogger(__name__)


@register.filter(name="id2contextvalue")
def id2contextvalue(id_input, request):
    try:
        value = request.context.get(id_input, None)
        return value if value is not None else ""
    except Exception as e:
        _logger.error(e)
        return ""
