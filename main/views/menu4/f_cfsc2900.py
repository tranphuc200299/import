import logging
from django.db import transaction
from django.shortcuts import render
from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute
from main.common.function.Common import DbDataChange, sqlStringConvert
from main.common.function.Const import NOMAL_OK, FATAL_ERR
from main.common.utils import Response

__logger = logging.getLogger(__name__)

PROGID = "cfsm2900"
CFSC29_MODE0 = 0
CFSC29_MODE1 = 1
CFSC29_LBL_MAX = 41
CFSC29_DAYKBN_WEK = ""
CFSC29_DAYKBN_SAT = "土曜"
CFSC29_DAYKBN_SUN = "日曜"
CFSC29_DAYKBN_HOL = "祝日"
CFSC29_DAYKBN_COL_WEK = "&HFFC0C0"
CFSC29_DAYKBN_COL_SAT = "&HFF8080"
CFSC29_DAYKBN_COL_SUN = "&H8080FF"
CFSC29_DAYKBN_COL_HOL = "&H8080FF"
CFSC29_YEAR_MIN = 1
CFSC29_YEAR_MAX = 12



@update_context()
@load_cfs_ini("menu4")
def f_cfsc2900(request):
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "txt_ayear_Change":
            id_show_data = txt_ayear_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_amonth_Change":
            id_show_data = txt_amonth_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_ayear_LostFocus":
            id_show_data = txt_ayear_LostFocus(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_amonth_LostFocus":
            id_show_data = txt_amonth_LostFocus(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_adaytp_Click":
            id_show_data = txt_adaytp_Click(request)
            return Response(request).json_response_event_js_html(id_show_data)
    else:
        Form_Load(request)

    return render(request, "menu/menu4/f_cfsc2900.html", request.context)

def Form_Load(request):
    try:
        init_form(request, CFSC29_MODE0)

        request.context["cmd_entry_enable"] = False
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
    except Exception as e:
        __logger.error(e)
        # TODO
        # OraError("", "")

def init_form(request, intMode):
    if intMode == CFSC29_MODE0:
        request.context["txt_ayear"] = ""

def inpdatachk1(request):
    if not request.context["txt_ayear"]:
        # TODO
        # MsgDspWarning "必須入力エラー", "本船コードを入力して下さい。"
        request.context["gSetField"] = "txt_ayear"
        return FATAL_ERR
    if not request.context["txt_amonth"]:
        # TODO
        # MsgDspWarning "必須入力エラー", "本船コードを入力して下さい。"
        request.context["gSetField"] = "txt_amonth"
        return FATAL_ERR
    return NOMAL_OK

def txt_ayear_LostFocus(request):
    if not request.context["txt_ayear"]:
        # TODO
        # MsgDspWarning "年数字チェック。"
        if not (request.context["txt_ayear"]).isnumeric():
            # TODO
            # MsgDspWarning "入力整合性エラー", "年は整数(9999形式)で入力して下さい。"
            request.context["gSetField"] = "txt_ayear"
            return FATAL_ERR
    return NOMAL_OK


def txt_amonth_LostFocus(request):
    if not request.context["txt_amonth"]:
        # TODO
        # MsgDspWarning "月数字チェック。"
        if not (request.context["txt_amonth"]).isnumeric():
            # TODO
            # MsgDspWarning "入力整合性エラー", "月は整数(9999形式)で入力して下さい。"
            request.context["gSetField"] = "txt_amonth"
            return FATAL_ERR
        if CFSC29_YEAR_MIN > int(request.context["txt_amonth"]) or CFSC29_YEAR_MAX < int(request.context["txt_amonth"]):
            # TODO
            # MsgDspWarning "入力整合性エラー", "月は" + str(CFSC29_YEAR_MIN) + "から" + str(CFSC29_YEAR_MAX) + "まで入力して下さい。"
            request.context["gSetField"] = "txt_amonth"
            return FATAL_ERR
    return NOMAL_OK

def inpdatachk2(request):
    return NOMAL_OK

def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False

    init_form(request, CFSC29_MODE0)
    request.context["gSetField"] = "txt_avesselcd"

def txt_ayear_Change(request):
    request.context["txt_ayear"] = request.context["txt_ayear"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_ayear", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]

def txt_amonth_Change(request):
    request.context["txt_amonth"] = request.context["txt_amonth"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_amonth", "cmd_entry_enable", "cmd_change"]