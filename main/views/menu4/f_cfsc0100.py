import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute
from main.common.function.Common import sqlStringConvert, IsNumeric
from main.common.function.Const import NOMAL_OK, FATAL_ERR
from main.common.utils import Response

PROGID = "cfsm0100"

@update_context()
@load_cfs_ini("menu4")
def f_cfsc0100(request):
    return render(request, "menu/menu4/f_cfsc0100.html", request.context)







