import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute, Const
from main.common.function.Common import dbField, DbDataChange, dbField
from main.common.function.Const import FATAL_ERR, NOMAL_OK, MSG_DSP_ERROR
from main.common.function.DspMessage import MsgDspError
from main.common.utils import Response
from main.middleware.exception.exceptions import PostgresException

__logger = logging.getLogger(__name__)

PROGID = "cfsm0900"
CFSC09_MODE0 = 0
CFSC09_MODE1 = 1


@update_context()
@load_cfs_ini("menu4")
def f_cfsc0900(request):
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "cmd_search":
            cmd_search_Click(request)
        elif action == "cmd_change":
            cmd_change_Click(request)
        elif action == "cmd_delete":
            cmd_delete_Click(request)
        elif action == "cmd_entry":
            cmd_entry_Click(request)
        elif action == "cmd_cancel":
            cmd_cancel_Click(request)
        elif action == "txt_aportcd_Change":
            id_show_data = txt_aportcd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_aareacd_Change":
            id_show_data = txt_aareacd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
    else:
        Form_Load(request)
    return render(request, 'menu/menu4/f_cfsc0900.html', request.context)


def Form_Load(request):
    init_form(request, CFSC09_MODE0)
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"


def init_form(request, intMode):
    if intMode == CFSC09_MODE0:
        request.context["txt_aportcd"] = ""
    request.context["txt_aportnm"] = ""
    request.context["txt_aareacd"] = ""


def inpdatachk1(request):
    if request.context["txt_aportcd"] == "":
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "ポート名称を入力して下さい。")
        request.context["gSetField"] = "txt_aportcd"
        return FATAL_ERR
    return NOMAL_OK


def inpdatachk2(request):
    if request.context["txt_aportnm"] == "":
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "ポート名称を入力して下さい。")
        request.context["gSetField"] = "txt_aportnm"
        return FATAL_ERR
    if len(request.context["txt_aportnm"]) > 25:
        MsgDspError(request, Const.MSG_DSP_WARN, "入力桁数エラー", "ポート名称は" + "25" + "桁以内で入力して下さい。")
        request.context["gSetField"] = "txt_aportnm"
        return FATAL_ERR
    return NOMAL_OK


def cmd_change_Click(request):
    sql = ""
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return

        sql += "UPDATE TBPORT" + request.cfs_ini["iniUpdTbl"]
        sql += " SET PORTNM = " + dbField(request.context["txt_aportnm"]) + ","
        sql += " AREACD = " + dbField(request.context["txt_aareacd"]) + ","
        sql += " UDATE = CURRENT_TIMESTAMP" + ","
        sql += " UWSID = " + dbField(request.cfs_ini["iniWsNo"]) + " "
        sql += " WHERE PORTCD = " + dbField(request.context["txt_aportcd"])
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC09_MODE0)
        request.context["gSetField"] = "txt_aportcd"
    except Exception as e:
        request.context["cmd_entry_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBPORT" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_delete_Click(request):
    try:
        with transaction.atomic():
            sql = "DELETE FROM TBPORT" + request.cfs_ini["iniUpdTbl"]
            sql += " WHERE PORTCD = " + dbField(request.context["txt_aportcd"])
            SqlExecute(sql).execute()
        init_form(request, CFSC09_MODE0)
        request.context["gSetField"] = "txt_aportcd"
    except Exception as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBPORT" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_entry_Click(request):
    sql = ""
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return

        sql += "INSERT INTO TBPORT" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "(PORTCD,PORTNM,AREACD,UDATE,UWSID) "
        sql += "VALUES("
        sql += dbField(request.context["txt_aportcd"]) + ","
        sql += dbField(request.context["txt_aportnm"]) + ","
        sql += dbField(request.context["txt_aareacd"]) + ","
        sql += "CURRENT_TIMESTAMP" + ","
        sql += dbField(request.cfs_ini["iniWsNo"]) + ')'
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC09_MODE0)
        request.context["gSetField"] = "txt_aportcd"
    except Exception as e:
        request.context["cmd_entry_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBPORT" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_search_Click(request):
    sql = ""
    try:
        init_form(request, CFSC09_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql += "SELECT * "
        sql += " FROM TBPORT" + request.cfs_ini["iniUpdTbl"] + " "
        sql += " WHERE PORTCD = " + dbField(request.context["txt_aportcd"])
        sql += " FOR UPDATE NOWAIT"
        RsTbPort = SqlExecute(sql).all()
        if len(RsTbPort.Rows) == 0:
            request.context["cmd_entry_enable"] = "True"
        else:
            request.context["txt_aportnm"] = DbDataChange(RsTbPort.Rows[0]["portnm"])
            request.context["txt_aareacd"] = DbDataChange(RsTbPort.Rows[0]["areacd"])
            request.context["cmd_change_enable"] = "True"
            request.context["cmd_delete_enable"] = "True"

        request.context["gSetField"] = "txt_aportnm"
    except Exception as e:
        raise PostgresException(Error=e, DbTbl="TBPORT" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"
    init_form(request, CFSC09_MODE0)
    request.context["gSetField"] = "txt_aportcd"


def txt_aportcd_Change(request):
    request.context["txt_aportcd"] = request.context["txt_aportcd"].upper()
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"
    return ["txt_aportcd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def txt_aareacd_Change(request):
    request.context["txt_aareacd"] = request.context["txt_aareacd"].upper()
    return "txt_aareacd"
