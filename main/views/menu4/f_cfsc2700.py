import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute, Const
from main.common.function.Common import dbField, DbDataChange
from main.common.function.Const import FATAL_ERR, NOMAL_OK
from main.common.function.DspMessage import MsgDspError
from main.common.utils import Response
from main.middleware.exception.exceptions import PostgresException

__logger = logging.getLogger(__name__)

PROGID = "cfsm2700"
CFSC27_MODE0 = 0
CFSC27_MODE1 = 1

@update_context()
@load_cfs_ini("menu4")
def f_cfsc2700(request):
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "txt_ainlandcd_Change":
            id_show_data = txt_ainlandcd_Change(request)
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
    return render(request, "menu/menu4/f_cfsc2700.html", request.context)


def Form_Load(request):
    try:
        init_form(request, CFSC27_MODE0)

        request.context["cmd_entry_enable"] = 'False'
        request.context["cmd_change_enable"] = 'False'
        request.context["cmd_delete_enable"] = 'False'
    except Exception as e:
        raise PostgresException(Error=e, DbTbl="", SqlStr="")

def txt_ainlandcd_Change(request):
    request.context["txt_ainlandcd"] = request.context["txt_ainlandcd"].upper()
    request.context["cmd_entry_enable"] = 'False'
    request.context["cmd_change_enable"] = 'False'
    request.context["cmd_delete_enable"] = 'False'
    return ["txt_ainlandcd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]

def cmd_search_Click(request):
    try:
        init_form(request, CFSC27_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql = "SELECT * "
        sql += " FROM TBINLAND" + request.cfs_ini["iniUpdTbl"]
        sql += " WHERE INLANDCD = " + dbField(request.context["txt_ainlandcd"])
        sql += " FOR UPDATE NOWAIT"
        RsTbPackg = SqlExecute(sql).all()
        if not RsTbPackg.Rows:
            request.context["cmd_entry_enable"] = 'True'
        else:
            request.context["txt_ainlandnm"] = DbDataChange(RsTbPackg.Rows[0]["inlandnm"])
            request.context["cmd_change_enable"] = 'True'
            request.context["cmd_delete_enable"] = 'True'
        request.context["gSetField"] = "txt_ainlandnm"
    except Exception as e:
        raise PostgresException(Error=e, DbTbl="TBINLAND" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)

def cmd_entry_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "INSERT INTO TBINLAND" + request.cfs_ini["iniUpdTbl"] + " "
            sql += "(INLANDCD,INLANDNM,UDATE,UWSID) "
            sql += "VALUES("
            sql += dbField(request.context["txt_ainlandcd"]) + ","
            sql += dbField(request.context["txt_ainlandnm"]) + ","
            sql += "CURRENT_TIMESTAMP" + ","
            sql += dbField(request.cfs_ini["iniWsNo"]) + ")"
            SqlExecute(sql).execute()
        init_form(request, CFSC27_MODE0)
        request.context["gSetField"] = "txt_ainlandcd"
    except Exception as e:
        request.context["cmd_entry_enable"] = 'False'
        raise PostgresException(Error=e, DbTbl="TBINLAND" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_change_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "UPDATE TBINLAND" + request.cfs_ini["iniUpdTbl"] + " "
            sql += "SET INLANDNM = " + dbField(request.context["txt_ainlandnm"]) + ","
            sql += "UDATE = CURRENT_TIMESTAMP" + ","
            sql += "UWSID = " + dbField(request.cfs_ini["iniWsNo"]) + " "
            sql += "WHERE INLANDCD = " + dbField(request.context["txt_ainlandcd"])
            SqlExecute(sql).execute()
        init_form(request, CFSC27_MODE0)
        request.context["gSetField"] = "txt_ainlandcd"
    except Exception as e:
        request.context["cmd_change_enable"] = 'False'
        request.context["cmd_delete_enable"] = 'False'
        raise PostgresException(Error=e, DbTbl="TBINLAND" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_delete_Click(request):
    try:
        with transaction.atomic():
            sql = "DELETE FROM TBINLAND" + request.cfs_ini["iniUpdTbl"] + " "
            sql += "WHERE INLANDCD = " + dbField(request.context["txt_ainlandcd"])
            SqlExecute(sql).execute()
        init_form(request, CFSC27_MODE0)
        request.context["gSetField"] = "txt_ainlandcd"
    except Exception as e:
        request.context["cmd_change_enable"] = 'False'
        request.context["cmd_delete_enable"] = 'False'
        raise PostgresException(Error=e, DbTbl="TBINLAND" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = 'False'
    request.context["cmd_change_enable"] = 'False'
    request.context["cmd_delete_enable"] = 'False'

    init_form(request, CFSC27_MODE0)
    request.context["gSetField"] = "txt_ainlandcd"


def init_form(request, intMode):
    if intMode == CFSC27_MODE0:
        request.context["txt_ainlandcd"] = ""
    request.context["txt_ainlandnm"] = ""


def inpdatachk1(request):
    if request.context["txt_ainlandcd"] == "":
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "搬入出先コードを入力して下さい。")
        request.context["gSetField"] = "txt_ainlandcd"
        return FATAL_ERR
    return NOMAL_OK


def inpdatachk2(request):
    if request.context["txt_ainlandnm"] == "":
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "搬入出先名称を入力して下さい。")
        request.context["gSetField"] = "txt_ainlandnm"
        return FATAL_ERR
    if 30 < len(request.context["txt_ainlandnm"]):
        MsgDspError(request, Const.MSG_DSP_WARN, "入力桁数エラー", "搬入出先名称は30桁以内で入力して下さい。")
        request.context["gSetField"] = "txt_ainlandnm"
        return FATAL_ERR
    return NOMAL_OK
