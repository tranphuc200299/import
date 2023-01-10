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
        elif action == "cmd_search":
            cmd_search_Click(request)
        elif action == "cmd_entry":
            cmd_entry_Click(request)
        elif action == "cmd_change":
            cmd_change_Click(request)
        elif action == "cmd_delete":
            cmd_delete_Click(request)
        elif action == "cmd_cancel":
            cmd_cancel_Click(request)
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


def cmd_search_Click(request):
    try:
        init_form(request, CFSC29_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql = "SELECT * "
        sql += "FROM TBVESSEL" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "WHERE VESSELCD = " + sqlStringConvert(request.context["txt_ayear"])
        sql += " FOR UPDATE NOWAIT"

        RsTbVessel = SqlExecute(sql).all()
        if not RsTbVessel.Rows:
            request.context["cmd_entry_enable"] = True
        else:
            request.context["txt_avesselnm"] = DbDataChange(RsTbVessel.Rows[0]["vesselnm"])
            request.context["txt_acallsign"] = DbDataChange(RsTbVessel.Rows[0]["callsign"])
            request.context["txt_aopecd"] = DbDataChange(RsTbVessel.Rows[0]["opecd"])
            RsTbOpe = Cm_TbOpeChk(request, request.context["txt_aopecd"])
            if RsTbOpe.Rows:
                request.context["lbl_aopenm"] = DbDataChange(RsTbOpe.Rows[0]["openm"])
            request.context["txt_alportcd"] = DbDataChange(RsTbVessel.Rows[0]["lportcd"])
            RsTbPort = Cm_TbPortChk(request, request.context["txt_alportcd"])
            if RsTbPort.Rows:
                request.context["lbl_aportnm"] = DbDataChange(RsTbPort.Rows[0]["portnm"])
            request.context["txt_aberthnm"] = DbDataChange(RsTbVessel.Rows[0]["berthnm"])
            request.context["txt_aline"] = DbDataChange(RsTbVessel.Rows[0]["line"])
            request.context["cmd_change_enable"] = True
            request.context["cmd_delete_enable"] = True
        request.context["gSetField"] = "txt_avesselnm"
    except Exception as e:
        __logger.error(e)
        raise Exception(e)
        # TODO
        # OraError "TBVESSEL" & strProcTbl, sql

def inpdatachk1(request):
    if not request.context["txt_ayear"]:
        # TODO
        # MsgDspWarning "必須入力エラー", "本船コードを入力して下さい。"
        request.context["gSetField"] = "txt_ayear"
        return FATAL_ERR
    return NOMAL_OK

def cmd_entry_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return

        sql = "INSERT INTO TBVESSEL" + request.cfs_ini["iniUpdTbl"] + ' '
        sql += "(VESSELCD,VESSELNM,CALLSIGN,OPECD,LPORTCD,BERTHNM,LINE,UDATE,UWSID) "
        sql += 'VALUES('
        sql += sqlStringConvert(request.context["txt_avesselcd"]) + ","
        sql += sqlStringConvert(request.context["txt_avesselnm"]) + ","
        sql += sqlStringConvert(request.context["txt_acallsign"]) + ","
        sql += sqlStringConvert(request.context["txt_aopecd"]) + ","
        sql += sqlStringConvert(request.context["txt_alportcd"]) + ","
        sql += sqlStringConvert(request.context["txt_aberthnm"]) + ","
        sql += sqlStringConvert(request.context["txt_aline"]) + ","
        sql += 'CURRENT_TIMESTAMP' + ","
        sql += sqlStringConvert(request.cfs_ini["iniWsNo"]) + ')'
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC29_MODE0)
        request.context["gSetField"] = "txt_avesselcd"
    except Exception as e:
        __logger.error(e)
        request.context["cmd_entry_enable"] = False
        raise Exception(e)
        # TODO
        # OraError "TBVESSEL" & strProcTbl, sql

def inpdatachk2(request):
    return NOMAL_OK

def cmd_change_Click(request):
    try:
        sql = "UPDATE TBVESSEL" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "SET VESSELNM = " + sqlStringConvert(request.context["txt_avesselnm"]) + ","
        sql += "CALLSIGN = " + sqlStringConvert(request.context["txt_acallsign"]) + ","
        sql += "OPECD = " + sqlStringConvert(request.context["txt_aopecd"]) + ","
        sql += "LPORTCD = " + sqlStringConvert(request.context["txt_alportcd"]) + ","
        sql += "BERTHNM = " + sqlStringConvert(request.context["txt_aberthnm"]) + ","
        sql += "LINE = " + sqlStringConvert(request.context["txt_aline"]) + ","
        sql += "UDATE = CURRENT_TIMESTAMP" + ","
        sql += "UWSID = " + sqlStringConvert(request.cfs_ini["iniWsNo"]) + " "
        sql += "WHERE VESSELCD = " + sqlStringConvert(request.context["txt_avesselcd"])
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC29_MODE0)
        request.context["gSetField"] = "txt_avesselcd"

    except Exception as e:
        __logger.error(e)
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise Exception(e)
        # TODO
        # OraError "TBVESSEL" & strProcTbl, sql

def cmd_delete_Click(request):
    sql = 'DELETE FROM TBVESSEL' + request.cfs_ini["iniUpdTbl"] + ' '
    sql += 'WHERE VESSELCD = ' + sqlStringConvert(request.context["txt_avesselcd"])
    try:
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC29_MODE0)
        request.context["gSetField"] = "txt_aopecd"
    except Exception as e:
        __logger.error(e)
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise Exception(e)
        # TODO
        # OraError "TBVESSEL" & strProcTbl, sql

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