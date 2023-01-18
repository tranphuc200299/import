import logging

from django.db import transaction, IntegrityError
from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute, Const
from main.common.function.Common import DbDataChange, dbField
from main.common.function.Const import NOMAL_OK, FATAL_ERR
from main.common.function.DspMessage import MsgDspError
from main.common.utils import Response
from main.middleware.exception.exceptions import PostgresException

__logger = logging.getLogger(__name__)

PROGID = "cfsm2100"
CFSC21_MODE0 = 0
CFSC21_MODE1 = 1


@update_context()
@load_cfs_ini("menu4")
def f_cfsc2100(request):
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
        elif action == "txt_anacgymcd_Change":
            id_show_data = txt_anacgymcd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_aprmsybt_Change":
            id_show_data = txt_aprmsybt_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
    else:
        Form_Load(request)
    return render(request, "menu/menu4/f_cfsc2100.html", request.context)


def Form_Load(request):
    init_form(request, CFSC21_MODE0)
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"


def txt_anacgymcd_Change(request):
    request.context["txt_anacgymcd"] = request.context["txt_anacgymcd"].upper()
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"
    return ["txt_anacgymcd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def txt_aprmsybt_Change(request):
    request.context["txt_aprmsybt"] = request.context["txt_aprmsybt"].upper()
    return "txt_aprmsybt"


def cmd_search_Click(request):
    sql = ""
    try:
        init_form(request, CFSC21_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql += "SELECT * "
        sql += "FROM TBPRMSYBTH" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "WHERE NACGYMCD = " + dbField(request.context["txt_anacgymcd"])
        sql += " FOR UPDATE NOWAIT"

        RsTbPrmsybth = SqlExecute(sql).all()
        if not RsTbPrmsybth.Rows:
            request.context["cmd_entry_enable"] = "True"
        else:
            request.context["txt_aprmsybt"] = DbDataChange(RsTbPrmsybth.Rows[0]["prmsybt"])
            request.context["txt_aprmsybtnm"] = DbDataChange(RsTbPrmsybth.Rows[0]["prmsybtnm"])
            request.context["cmd_change_enable"] = "True"
            request.context["cmd_delete_enable"] = "True"
        request.context["gSetField"] = "txt_aprmsybt"
    except IntegrityError as e:
        raise PostgresException(Error=e, DbTbl="TBPRMSYBTH" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)
    except Exception as e:
        __logger.error(e)
        raise Exception(e)


def cmd_entry_Click(request):
    sql = ""
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        sql = "INSERT INTO TBPRMSYBTH" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "(NACGYMCD,PRMSYBT,PRMSYBTNM,UDATE,UWSID) "
        sql += "VALUES("
        sql += dbField(request.context["txt_anacgymcd"]) + ","
        sql += dbField(request.context["txt_aprmsybt"]) + ","
        sql += dbField(request.context["txt_aprmsybtnm"]) + ","
        sql += "CURRENT_TIMESTAMP" + ","
        sql += dbField(request.cfs_ini["iniWsNo"]) + ')'
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC21_MODE0)
        request.context["gSetField"] = "txt_anacgymcd"
    except IntegrityError as e:
        request.context["cmd_entry_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBPRMSYBTH" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)
    except Exception as e:
        request.context["cmd_entry_enable"] = "False"
        __logger.error(e)
        raise Exception(e)


def cmd_change_Click(request):
    sql = ""
    try:
        sql = "UPDATE TBPRMSYBTH" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "SET PRMSYBT = " + dbField(request.context["txt_aprmsybt"]) + ","
        sql += "PRMSYBTNM = " + dbField(request.context["txt_aprmsybtnm"]) + ","
        sql += "UDATE = CURRENT_TIMESTAMP" + ","
        sql += "UWSID = " + dbField(request.cfs_ini["iniWsNo"]) + " "
        sql += "WHERE NACGYMCD = " + dbField(request.context["txt_anacgymcd"])
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC21_MODE0)
        request.context["gSetField"] = "txt_anacgymcd"

    except IntegrityError as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBPRMSYBTH" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)
    except Exception as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        __logger.error(e)
        raise Exception(e)


def cmd_delete_Click(request):
    sql = "DELETE FROM TBPRMSYBTH" + request.cfs_ini["iniUpdTbl"] + " "
    sql += "WHERE NACGYMCD = " + dbField(request.context["txt_anacgymcd"])
    try:
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC21_MODE0)
        request.context["gSetField"] = "txt_anacgymcd"
    except IntegrityError as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBPRMSYBTH" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)
    except Exception as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        __logger.error(e)
        raise Exception(e)


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"
    init_form(request, CFSC21_MODE0)
    request.context["gSetField"] = "txt_anacgymcd"


def init_form(request, intMode):
    if intMode == CFSC21_MODE0:
        request.context["txt_anacgymcd"] = ""
    request.context["txt_aprmsybt"] = ""
    request.context["txt_aprmsybtnm"] = ""


def inpdatachk1(request):
    if not request.context["txt_anacgymcd"]:
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "ＮＡＣＣＳ業務コードを入力して下さい。")
        request.context["gSetField"] = "txt_anacgymcd"
        return FATAL_ERR
    return NOMAL_OK


def inpdatachk2(request):
    if request.context["txt_aprmsybt"] == '':
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "申告種別コードを入力して下さい。")
        request.context["gSetField"] = "txt_aprmsybt"
        return FATAL_ERR

    if request.context["txt_aprmsybtnm"] != "":
        if len(request.context["txt_aprmsybtnm"]) > 25:
            MsgDspError(request, Const.MSG_DSP_WARN, "入力桁数エラー", "申告種別名称は25桁以内で入力して下さい。")
            request.context["gSetField"] = "txt_aprmsybtnm"
            return FATAL_ERR
    return NOMAL_OK
