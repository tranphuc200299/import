import logging
from django.db import IntegrityError, transaction
from django.shortcuts import render
from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute
from main.common.function.Common import DbDataChange, sqlStringConvert, dbField
from main.common.function.DspMessage import MsgDspError
from main.common.function.Const import NOMAL_OK, FATAL_ERR, DB_NOT_FIND, DB_FATAL_ERR, MSG_DSP_ERROR, MSG_DSP_WARN
from main.common.function.TableCheck import TbOpe_TableCheck, TbPort_TableCheck
from main.common.utils import Response
from main.middleware.exception.exceptions import (
    PostgresException
)

__logger = logging.getLogger(__name__)

PROGID = "cfsm1100"
CFSC11_MODE0 = 0
CFSC11_MODE1 = 1


@update_context()
@load_cfs_ini("menu4")
def f_cfsc1100(request):
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "cmd_search":
            cmd_search_Click(request)
        elif action == "cmd_entry":
            cmd_entry_Click(request)
        elif action == "cmd_change":
            cmd_change_Click(request)
        elif action == "cmd_cancel":
            cmd_cancel_Click(request)
        elif action == "cmd_delete":
            cmd_delete_Click(request)
        elif action == "txt_aopecd_Change":
            id_show_data = txt_aopecd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_asportcd_Change":
            id_show_data = txt_asportcd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_aportcd_Change":
            id_show_data = txt_aportcd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_aportcd_LostFocus":
            id_show_data = txt_aportcd_LostFocus(request)
            return Response(request).json_response_event_js_html(id_show_data)
    else:
        Form_Load(request)
    return render(request, "menu/menu4/f_cfsc1100.html", request.context)


def Form_Load(request):
    init_form(request, CFSC11_MODE0)
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"


def init_form(request, intMode):
    if intMode == CFSC11_MODE0:
        request.context["txt_aopecd"] = ""
        request.context["txt_asportcd"] = ""

    request.context["txt_aportcd"] = ""
    request.context["lbl_aportnm"] = ""


def txt_aportcd_LostFocus(request):
    RsTbPort = Cm_TbPortChk(request, request.context["txt_aportcd"])
    if not RsTbPort.Rows:
        MsgDspError(request, MSG_DSP_ERROR, "コード未登録エラー", "Port Code Tableが存在しません。")
        request.context["gSetField"] = "txt_aportcd"
        return request.context["gSetField"]
    else:
        request.context["lbl_aportnm"] = DbDataChange(RsTbPort.Rows[0]["portnm"])
        return "lbl_aportnm"


def txt_asportcd_Change(request):
    request.context["txt_asportcd"] = request.context["txt_asportcd"].upper()
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"
    return ["txt_asportcd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def txt_aopecd_Change(request):
    request.context["txt_aopecd"] = request.context["txt_aopecd"].upper()
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"
    return ["txt_aopecd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def txt_aportcd_Change(request):
    request.context["txt_aportcd"] = request.context["txt_aportcd"].upper()
    return ["txt_aportcd"]


def Cm_TbPortChk(request, strPortCd):
    sql = ""
    try:
        sql = "SELECT PORTNM "
        sql += "FROM TBPORT" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "WHERE PORTCD = " + sqlStringConvert(strPortCd)
        return SqlExecute(sql).all()
    except IntegrityError as e:
        raise PostgresException(Error=e, DbTbl="TBPORT" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def inpdatachk1(request):
    if not request.context["txt_aopecd"]:
        MsgDspError(request, MSG_DSP_WARN, "必須入力エラー", "オペレータコードを入力して下さい。")
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR
    intRtn = TbOpe_TableCheck(request.context["txt_aopecd"], request.cfs_ini["iniUpdTbl"])
    if intRtn == DB_NOT_FIND:
        MsgDspError(request, MSG_DSP_WARN, "コード未登録エラー", "Operator Code Tableが登録されていません。")
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR
    elif intRtn == DB_FATAL_ERR:
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR
    return NOMAL_OK


def cmd_search_Click(request):
    sql = ""
    try:
        init_form(request, CFSC11_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql = "SELECT * "
        sql += "FROM TBSPORT" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "WHERE OPECD = " + dbField(request.context["txt_aopecd"])
        sql += " AND SPORTCD = " + dbField(request.context["txt_asportcd"])
        sql += " FOR UPDATE NOWAIT"
        RsTbSPort = SqlExecute(sql).all()
        if not RsTbSPort.Rows:
            request.context["cmd_entry_enable"] = "True"
        else:
            request.context["txt_aportcd"] = DbDataChange(RsTbSPort.Rows[0]["portcd"])
            RsTbPort = Cm_TbPortChk(request, request.context["txt_aportcd"])
            if RsTbPort.Rows:
                request.context["lbl_aportnm"] = DbDataChange(RsTbPort.Rows[0]["portnm"])
            request.context["cmd_change_enable"] = "True"
            request.context["cmd_delete_enable"] = "True"
        request.context["gSetField"] = "txt_aportcd"
    except IntegrityError as e:
        raise PostgresException(Error=e, DbTbl="TBSPORT" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def inpdatachk2(request):
    if request.context["txt_aportcd"] == '':
        MsgDspError(request, MSG_DSP_WARN, "必須入力エラー", "ポートコードを入力して下さい。")
        request.context["gSetField"] = "txt_aportcd"
        return FATAL_ERR
    intRtn = TbPort_TableCheck(request.context["txt_aportcd"],  request.cfs_ini["iniUpdTbl"])
    if intRtn == DB_NOT_FIND:
        MsgDspError(request, MSG_DSP_WARN, "コード未登録エラー", "Port Code Tableが登録されていません。")
        request.context["gSetField"] = "txt_aportcd"
        return FATAL_ERR
    elif intRtn == DB_FATAL_ERR:
        request.context["gSetField"] = "txt_aportcd"
        return FATAL_ERR
    return NOMAL_OK


def cmd_entry_Click(request):
    sql = ""
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        sql = "INSERT INTO TBSPORT" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "(OPECD,SPORTCD,PORTCD,UDATE,UWSID) "
        sql += "VALUES("
        sql += dbField(request.context["txt_aopecd"]) + ","
        sql += dbField(request.context["txt_asportcd"]) + ","
        sql += dbField(request.context["txt_aportcd"]) + ","
        sql += "CURRENT_TIMESTAMP,"
        sql += dbField(request.cfs_ini["iniWsNo"]) + ")"
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC11_MODE0)
        request.context["gSetField"] = "txt_aopecd"
    except IntegrityError as e:
        request.context["cmd_entry_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBSPORT" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)
    except Exception as e:
        request.context["cmd_entry_enable"] = "False"
        raise Exception(e)


def cmd_change_Click(request):
    sql = ""
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        sql = "UPDATE TBSPORT" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "SET PORTCD = " + dbField(request.context["txt_aportcd"]) + ","
        sql += "UDATE = CURRENT_TIMESTAMP" + ","
        sql += "UWSID = " + dbField(request.cfs_ini["iniWsNo"]) + " "
        sql += "WHERE OPECD = " + dbField(request.context["txt_aopecd"])
        sql += " AND SPORTCD = " + dbField(request.context["txt_asportcd"])
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC11_MODE0)
        request.context["gSetField"] = "txt_aopecd"
    except IntegrityError as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBSPORT" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)

    except Exception as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise Exception(e)


def cmd_delete_Click(request):
    sql = "DELETE FROM TBSPORT" + request.cfs_ini["iniUpdTbl"] + " "
    sql += "WHERE OPECD = " + dbField(request.context["txt_aopecd"])
    sql += " AND SPORTCD = " + dbField(request.context["txt_asportcd"])
    try:
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC11_MODE0)
        request.context["gSetField"] = "txt_aopecd"
    except IntegrityError as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBSPORT" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)
    except Exception as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise Exception(e)


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"

    init_form(request, CFSC11_MODE0)
    request.context["gSetField"] = "txt_aopecd"
