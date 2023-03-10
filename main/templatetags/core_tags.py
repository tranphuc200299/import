import logging
from django import template
from django.urls import reverse_lazy
from main.common.function import Common
from main.common.utils import ConfigIni

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


@register.inclusion_tag('partials/header.html')
def header(request):
    config_ini = ConfigIni()
    names = config_ini.get_all_area_name()
    bond_area_name = Common.pfncDataSessionGet(request, "bond_area_name")
    path_url = request.resolver_match.url_name
    if path_url == "":
        path_url = "home"
    response = {
        "bond_area_names": names,
        "bond_area_name_selected": bond_area_name,
        "path_url": path_url,
        "request": request
    }
    return response


@register.filter(name="name2url")
def name2url(name_url):
    try:
        if name_url == "#":
            return name_url
        return str(reverse_lazy(name_url))
    except Exception as e:
        _logger.error(e)
        return ""


@register.filter(name="sq2any")
def sq2any(sequence, type):
    return f"txt_adaytp{sequence}_{type}"


@register.filter(name="id2stbutton")
def id2stbutton(id):
    return f"{id}_enable"


@register.filter(name="addTabIndex")
def addTabIndex(id, plus):
    return id + plus
