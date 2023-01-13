import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute
from main.common.function.Common import dbField, DbDataChange
from main.common.function.Const import FATAL_ERR, NOMAL_OK
from main.common.utils import Response
from main.middleware.exception.exceptions import PostgresException

__logger = logging.getLogger(__name__)

PROGID = "cfsm1500"
CFSC15_MODE0 = 0
CFSC15_MODE1 = 1

@update_context()
@load_cfs_ini("menu4")
def f_cfsc1500(request):
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "txt_apackcd_Change":
            id_show_data = txt_apackcd_Change(request)
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
    return render(request, "menu/menu4/f_cfsc1500.html", request.context)


def Form_Load(request):
    try:
        init_form(request, CFSC15_MODE0)

        request.context["cmd_entry_enable"] = False
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
    except Exception as e:
        raise PostgresException(Error=e, DbTbl="", SqlStr="")

def txt_apackcd_Change(request):
    request.context["txt_apackcd"] = request.context["txt_apackcd"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_apackcd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]

def cmd_search_Click(request):
    try:
        init_form(request, CFSC15_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql = "SELECT * "
        sql += " FROM TBPACKG" + request.cfs_ini["iniUpdTbl"]
        sql += " WHERE PAssCKCD = " + dbField(request.context["txt_apackcd"])
        sql += " FOR UPDATE NOWAIT"
        RsTbPackg = SqlExecute(sql).all()
        if not RsTbPackg.Rows:
            request.context["cmd_entry_enable"] = True
        else:
            request.context["txt_apacknm"] = DbDataChange(RsTbPackg.Rows[0]['packnm'])
            request.context["cmd_change_enable"] = True
            request.context["cmd_delete_enable"] = True
        request.context["gSetField"] = "txt_apacknm"
    except Exception as e:
        raise PostgresException(Error=e, DbTbl="TBPACKG" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_entry_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "INSERT INTO TBPACKG" + request.cfs_ini["iniUpdTbl"] + " "
            sql += "(PACKCD,PACKNM,UDATE,UWSID) "
            sql += "VALUES("
            sql += dbField(request.context["txt_apackcd"]) + ","
            sql += dbField(request.context["txt_apacknm"]) + ","
            sql += "CURRENT_TIMESTAMPsss" + ","
            sql += dbField(request.cfs_ini["iniWsNo"]) + ")"
            SqlExecute(sql).execute()
        init_form(request, CFSC15_MODE0)
        request.context["gSetField"] = "txt_apackcd"
    except Exception as e:
        raise PostgresException(Error=e, DbTbl="TBPACKG" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)

def cmd_change_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "UPDATE TBPACKG" + request.cfs_ini["iniUpdTbl"] + " "
            sql += "SET PACKNM = " + dbField(request.context["txt_apacknm"]) + ","
            sql += "UDATE = CURRENT_TIMESTAMP" + ","
            sql += "UWSID = " + dbField(request.cfs_ini["iniWsNo"]) + " "
            sql += "WHERE PACKCD = " + dbField(request.context["txt_apackcd"])
            SqlExecute(sql).execute()
        init_form(request, CFSC15_MODE0)
        request.context["gSetField"] = "txt_apackcd"
    except Exception as e:
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise PostgresException(Error=e, DbTbl="TBPACKG" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_delete_Click(request):
    try:
        with transaction.atomic():
            sql = "DELETE FROM TBPACKG" + request.cfs_ini["iniUpdTbl"] + " "
            sql += "WHERE PACKCD = " + dbField(request.context["txt_apackcd"])
            SqlExecute(sql).execute()
        init_form(request, CFSC15_MODE0)
        request.context["gSetField"] = "txt_apackcd"
    except Exception as e:
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise PostgresException(Error=e, DbTbl="TBPACKG" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False

    init_form(request, CFSC15_MODE0)
    request.context["gSetField"] = "txt_apackcd"


def init_form(request, intMode):
    if intMode == CFSC15_MODE0:
        request.context["txt_apackcd"] = ""
    request.context["txt_apacknm"] = ""


def inpdatachk1(request):
    if request.context["txt_apackcd"] == "":
        request.context["lblMsg"] = "必須入力エラー荷姿コードを入力して下さい。"
        request.context["gSetField"] = "txt_apackcd"
        return FATAL_ERR
    return NOMAL_OK


def inpdatachk2(request):
    if request.context["txt_apacknm"] == "":
        request.context["lblMsg"] = "必須入力エラー荷姿名称を入力して下さい。"
        request.context["gSetField"] = "txt_apacknm"
        return FATAL_ERR
    if 25 < len(request.context["txt_apacknm"]):
        request.context["lblMsg"] = "入力桁数エラー荷姿名称は25桁以内で入力して下さい。"
        request.context["gSetField"] = "txt_apacknm"
        return FATAL_ERR
    return NOMAL_OK
