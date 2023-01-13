import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute, Const
from main.common.function.Common import dbField
from main.common.function.Const import FATAL_ERR, NOMAL_OK
from main.common.function.DspMessage import MsgDspError
from main.common.utils import Response
from main.middleware.exception.exceptions import PostgresException

__logger = logging.getLogger(__name__)

PROGID = "cfsm3100"
CFSC31_MODE0 = 0
CFSC31_MODE1 = 1


@update_context()
@load_cfs_ini("menu4")
def f_cfsc3100(request):
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "txt_aszouchicd_Change":
            id_show_data = txt_aszouchicd_Change(request)
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
    return render(request, "menu/menu4/f_cfsc3100.html", request.context)


def Form_Load(request):
    try:
        init_form(request, CFSC31_MODE0)

        request.context["cmd_entry_enable"] = False
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
    except Exception as e:
        __logger.error(e)
        # TODO
        # OraError("", "")


def txt_aszouchicd_Change(request):
    request.context["txt_aszouchicd"] = request.context["txt_aszouchicd"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_aszouchicd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def cmd_search_Click(request):
    sql = ""
    try:
        init_form(request, CFSC31_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql += "SELECT * "
        sql += " FROM TBSZOUCHI" + request.cfs_ini["iniUpdTbl"]
        sql += " WHERE SZOUCHICD = " + dbField(request.context["txt_aszouchicd"])
        sql += " FOR UPDATE NOWAIT"
        RsTbSZouchi = SqlExecute(sql).all()
        if not RsTbSZouchi.Rows:
            request.context["cmd_entry_enable"] = True
        else:
            # TODO
            request.context["txt_aszouchinm"] = RsTbSZouchi.Rows[0]['szouchinm']
            request.context["cmd_change_enable"] = True
            request.context["cmd_delete_enable"] = True
        request.context["gSetField"] = "txt_aszouchinm"
    except Exception as e:
        raise PostgresException(Error=e, DbTbl="TBSZOUCHI" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_entry_Click(request):
    try:
        if inpdatachk1(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "INSERT INTO TBSZOUCHI" + request.cfs_ini["iniUpdTbl"] + " "
            sql += "(SZOUCHICD,SZOUCHINM,UDATE,UWSID) "
            sql += "VALUES("
            sql += dbField(request.context["txt_aszouchicd"]) + ","
            sql += dbField(request.context["txt_aszouchinm"]) + ","
            sql += "CURRENT_TIMESTAMP" + ","
            sql += dbField(request.cfs_ini["iniWsNo"]) + ")"
            SqlExecute(sql).execute()
        init_form(request, CFSC31_MODE0)
        request.context["gSetField"] = "txt_aszouchicd"
    except Exception as e:
        request.context["cmd_entry_enable"] = False
        raise PostgresException(Error=e, DbTbl="TBSZOUCHI" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_change_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "UPDATE TBSZOUCHI" + request.cfs_ini["iniUpdTbl"] + " "
            sql += "SET SZOUCHINM = " + dbField(request.context["txt_aszouchinm"]) + ","
            sql += "UDATE = CURRENT_TIMESTAMP" + ","
            sql += "UWSID = " + dbField(request.cfs_ini["iniWsNo"]) + " "
            sql += "WHERE SZOUCHICD = " + dbField(request.context["txt_aszouchicd"])
            SqlExecute(sql).execute()
        init_form(request, CFSC31_MODE0)
        request.context["gSetField"] = "txt_aszouchicd"
    except Exception as e:
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise PostgresException(Error=e, DbTbl="TBSZOUCHI" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_delete_Click(request):
    try:
        with transaction.atomic():
            sql = "DELETE FROM TBSZOUCHI" + request.cfs_ini["iniUpdTbl"] + " "
            sql += "WHERE SZOUCHICD = " + dbField(request.context["txt_aszouchicd"])
            SqlExecute(sql).execute()
        init_form(request, CFSC31_MODE0)
        request.context["gSetField"] = "txt_aszouchicd"
    except Exception as e:
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise PostgresException(Error=e, DbTbl="TBSZOUCHI" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False

    init_form(request, CFSC31_MODE0)
    request.context["gSetField"] = "txt_aszouchicd"


def init_form(request, intMode):
    if intMode == CFSC31_MODE0:
        request.context["txt_aszouchicd"] = ""
    request.context["txt_aszouchinm"] = ""


def inpdatachk1(request):
    if request.context["txt_aszouchicd"] == "":
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "倉庫内蔵置場所コードを入力して下さい。")
        request.context["gSetField"] = "txt_aszouchicd"
        return FATAL_ERR
    return NOMAL_OK


def inpdatachk2(request):
    if request.context["txt_aszouchinm"] == "":
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "倉庫内蔵置場所名称を入力して下さい。")
        request.context["gSetField"] = "txt_aszouchinm"
        return FATAL_ERR
    if 20 < len(request.context["txt_aszouchinm"]):
        MsgDspError(request, Const.MSG_DSP_WARN, "入力桁数エラー", "倉庫内蔵置場所名称は" + "20" + "桁以内で入力して下さい。")
        return FATAL_ERR
    return NOMAL_OK
