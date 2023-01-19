import logging
from django.db import transaction
from django.shortcuts import render
from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute, Const
from main.common.function.Common import dbField, DbDataChange
from main.common.function.Const import NOMAL_OK, FATAL_ERR
from main.common.function.DspMessage import MsgDspError
from main.common.utils import Response
from main.middleware.exception.exceptions import PostgresException

__logger = logging.getLogger(__name__)

PROGID = 'cfsm1300'
CFSC13_MODE0 = 0
CFSC13_MODE1 = 1


@update_context()
@load_cfs_ini("menu4")
def f_cfsc1300(request):
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
        elif action == "txt_afwdcd_Change":
            id_show_data = txt_afwdcd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
    else:
        Form_Load(request)
    return render(request, "menu/menu4/f_cfsc1300.html", request.context)


def Form_Load(request):
    init_form(request, CFSC13_MODE0)
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"


def txt_afwdcd_Change(request):
    request.context["txt_afwdcd"] = request.context["txt_afwdcd"].upper()
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"
    return ["txt_afwdcd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def cmd_search_Click(request):
    sql = ""
    try:
        init_form(request, CFSC13_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql += 'SELECT * '
        sql += 'FROM TBFORWARD' + request.cfs_ini["iniUpdTbl"] + ' '
        sql += 'WHERE FWDCD = ' + dbField(request.context["txt_afwdcd"])
        sql += ' FOR UPDATE NOWAIT'

        RsTbForward = SqlExecute(sql).all()
        if len(RsTbForward.Rows) == 0:
            request.context["cmd_entry_enable"] = "True"
        else:
            request.context["txt_afwdnm"] = DbDataChange(RsTbForward.Rows[0]["fwdnm"])
            request.context["txt_afwdtannm"] = DbDataChange(RsTbForward.Rows[0]["fwdtannm"])
            request.context["txt_afwdtel"] = DbDataChange(RsTbForward.Rows[0]["fwdtel"])
            request.context["txt_afwdfax"] = DbDataChange(RsTbForward.Rows[0]["fwdfax"])
            request.context["cmd_change_enable"] = "True"
            request.context["cmd_delete_enable"] = "True"
        request.context["gSetField"] = "txt_afwdnm"
    except Exception as e:
        raise PostgresException(Error=e, DbTbl="TBFORWARD" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_entry_Click(request):
    sql = ""
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return

        sql += 'INSERT INTO TBFORWARD' + request.cfs_ini["iniUpdTbl"] + ' '
        sql += '(FWDCD,FWDNM,FWDTANNM,FWDTEL,FWDFAX,UDATE,UWSID) '
        sql += 'VALUES('
        sql += dbField(request.context["txt_afwdcd"]) + ','
        sql += dbField(request.context["txt_afwdnm"]) + ','
        sql += dbField(request.context["txt_afwdtannm"]) + ','
        sql += dbField(request.context["txt_afwdtel"]) + ','
        sql += dbField(request.context["txt_afwdfax"]) + ','
        sql += 'CURRENT_TIMESTAMP' + ','
        sql += dbField(request.cfs_ini["iniWsNo"]) + ')'
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC13_MODE0)
        request.context["gSetField"] = "txt_afwdcd"
    except Exception as e:
        request.context["cmd_entry_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBFORWARD" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_change_Click(request):
    sql = ""
    try:
        sql += 'UPDATE TBFORWARD' + request.cfs_ini["iniUpdTbl"] + ' '
        sql += 'SET FWDNM = ' + dbField(request.context["txt_afwdnm"]) + ','
        sql += 'FWDTANNM = ' + dbField(request.context["txt_afwdtannm"]) + ','
        sql += 'FWDTEL = ' + dbField(request.context["txt_afwdtel"]) + ','
        sql += 'FWDFAX = ' + dbField(request.context["txt_afwdfax"]) + ','
        sql += 'UDATE = CURRENT_TIMESTAMP' + ','
        sql += 'UWSID = ' + dbField(request.cfs_ini["iniWsNo"]) + ' '
        sql += 'WHERE FWDCD = ' + dbField(request.context["txt_afwdcd"])
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC13_MODE0)
        request.context["gSetField"] = "txt_afwdcd"

    except Exception as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBFORWARD" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_delete_Click(request):
    sql = 'DELETE FROM TBFORWARD' + request.cfs_ini["iniUpdTbl"] + ' '
    sql += 'WHERE FWDCD = ' + dbField(request.context["txt_afwdcd"])
    try:
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC13_MODE0)
        request.context["gSetField"] = "txt_afwdcd"
    except Exception as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBFORWARD" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"

    init_form(request, CFSC13_MODE0)
    request.context["gSetField"] = "txt_afwdcd"


def init_form(request, intMode):
    if intMode == CFSC13_MODE0:
        request.context["txt_afwdcd"] = ""
    request.context["txt_afwdnm"] = ""
    request.context["txt_afwdtannm"] = ""
    request.context["txt_afwdtel"] = ""
    request.context["txt_afwdfax"] = ""


def inpdatachk1(request):
    if not request.context["txt_afwdcd"]:
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "海貨業者コードを入力して下さい。")
        request.context["gSetField"] = "txt_afwdcd"
        return FATAL_ERR
    return NOMAL_OK


def inpdatachk2(request):
    if request.context["txt_afwdnm"] == '':
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "海貨業者名称を入力して下さい。")
        request.context["gSetField"] = "txt_afwdnm"
        return FATAL_ERR
    if len(request.context["txt_afwdnm"]) > 60:
        MsgDspError(request, Const.MSG_DSP_WARN, "入力桁数エラー", "海貨業者名称は" + "60" + "桁以内で入力して下さい。")
        request.context["gSetField"] = "txt_afwdnm"
        return FATAL_ERR
    if len(request.context["txt_afwdtannm"]) > 10:
        MsgDspError(request, Const.MSG_DSP_WARN, "入力桁数エラー", "海貨業者担当者名称は" + "10" + "桁以内で入力して下さい。")
        request.context["gSetField"] = "txt_afwdtannm"
        return FATAL_ERR
    return NOMAL_OK
