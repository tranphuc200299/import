import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute
from main.common.function.Common import sqlStringConvert, IsNumeric, DbDataChange
from main.common.function.Const import NOMAL_OK, FATAL_ERR
from main.common.utils import Response

PROGID = "cfsm2300"
CFSC23_MODE0 = 0
CFSC23_MODE1 = 1
CFSC23_TANKA_MIN = 0
CFSC23_TANKA_MAX = 99999999

__logger = logging.getLogger(__name__)


@update_context()
@load_cfs_ini("menu4")
def f_cfsc2300(request):
    if request.method == "POST":
        action = request.POST.get("action", None)
    return render(request, "menu/menu4/f_cfsc2300.html", request.context)