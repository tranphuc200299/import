import logging
from django.db import transaction
from django.shortcuts import render
from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute
from main.common.function.Common import sqlStringConvert, DbDataChange
from main.common.function.Const import NOMAL_OK, FATAL_ERR
from main.common.utils import Response

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

    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False


def txt_afwdcd_Change(request):
    request.context["txt_afwdcd"] = request.context["txt_afwdcd"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_afwdcd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def cmd_search_Click(request):
    try:
        init_form(request, CFSC13_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql = 'SELECT * '
        sql += 'FROM TBFORWARD' + request.cfs_ini["iniUpdTbl"] + ' '
        sql += 'WHERE FWDCD = ' + sqlStringConvert(request.context["txt_afwdcd"])
        sql += ' FOR UPDATE NOWAIT'

        RsTbForward = SqlExecute(sql).all()
        if not RsTbForward.Rows:
            request.context["cmd_entry_enable"] = True
        else:
            request.context["txt_afwdnm"] = DbDataChange(RsTbForward.Rows[0]["fwdnm"])
            request.context["txt_afwdtannm"] = DbDataChange(RsTbForward.Rows[0]["fwdtannm"])
            request.context["txt_afwdtel"] = DbDataChange(RsTbForward.Rows[0]["fwdtel"])
            request.context["txt_afwdfax"] = DbDataChange(RsTbForward.Rows[0]["fwdfax"])
            request.context["cmd_change_enable"] = True
            request.context["cmd_delete_enable"] = True
        request.context["gSetField"] = "txt_afwdnm"
    except Exception as e:
        __logger.error(e)
        # TODO
        # OraError "TBFORWARD" & strProcTbl, sql


def cmd_entry_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return

        sql = 'INSERT INTO TBFORWARD' + request.cfs_ini["iniUpdTbl"] + ' '
        sql += '(FWDCD,FWDNM,FWDTANNM,FWDTEL,FWDFAX,UDATE,UWSID) '
        sql += 'VALUES('
        sql += sqlStringConvert(request.context["txt_afwdcd"]) + ','
        sql += sqlStringConvert(request.context["txt_afwdnm"]) + ','
        sql += sqlStringConvert(request.context["txt_afwdtannm"]) + ','
        sql += sqlStringConvert(request.context["txt_afwdtel"]) + ','
        sql += sqlStringConvert(request.context["txt_afwdfax"]) + ','
        sql += 'CURRENT_TIMESTAMP' + ','
        sql += sqlStringConvert(request.cfs_ini["iniWsNo"]) + ')'
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC13_MODE0)
        request.context["gSetField"] = "txt_afwdcd"
    except Exception as e:
        __logger.error(e)
        request.context["cmd_entry_enable"] = False
        # TODO
        # OraError "TBFORWARD" & strProcTbl, sql


def cmd_change_Click(request):
    try:
        sql = 'UPDATE TBFORWARD' + request.cfs_ini["iniUpdTbl"] + ' '
        sql += 'SET FWDNM = ' + sqlStringConvert(request.context["txt_afwdnm"]) + ','
        sql += 'FWDTANNM = ' + sqlStringConvert(request.context["txt_afwdtannm"]) + ','
        sql += 'FWDTEL = ' + sqlStringConvert(request.context["txt_afwdtel"]) + ','
        sql += 'FWDFAX = ' + sqlStringConvert(request.context["txt_afwdfax"]) + ','
        sql += 'UDATE = CURRENT_TIMESTAMP' + ','
        sql += 'UWSID = ' + sqlStringConvert(request.cfs_ini["iniWsNo"]) + ' '
        sql += 'WHERE FWDCD = ' + sqlStringConvert(request.context["txt_afwdcd"])
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC13_MODE0)
        request.context["gSetField"] = "txt_afwdcd"

    except Exception as e:
        __logger.error(e)
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        # TODO
        # OraError "TBFORWARD" & strProcTbl, sql


def cmd_delete_Click(request):
    sql = 'DELETE FROM TBFORWARD' + request.cfs_ini["iniUpdTbl"] + ' '
    sql += 'WHERE FWDCD = ' + sqlStringConvert(request.context["txt_afwdcd"])
    try:
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC13_MODE0)
        request.context["gSetField"] = "txt_afwdcd"
    except Exception as e:
        __logger.error(e)
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        # TODO
        # OraError "TBFORWARD" & strProcTbl, sql


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False

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
        request.context["lblMsg"] = '必須入力エラー海貨業者コードを入力して下さい。'
        request.context["gSetField"] = "txt_afwdcd"
        return FATAL_ERR
    return NOMAL_OK


def inpdatachk2(request):
    if request.context["txt_afwdnm"] == '':
        request.context["lblMsg"] = '必須入力エラー海貨業者名称を入力して下さい。'
        request.context["gSetField"] = "txt_afwdnm"
        return FATAL_ERR
    if len(request.context["txt_afwdnm"]) > 60:
        request.context["lblMsg"] = '入力桁数エラー', '海貨業者名称は' + '60' + '桁以内で入力して下さい。'
        request.context["gSetField"] = "txt_afwdnm"
        return FATAL_ERR
    if len(request.context["txt_afwdtannm"]) > 10:
        request.context["lblMsg"] = '入力桁数エラー', '海貨業者担当者名称は' + '10' + '桁以内で入力して下さい。'
        request.context["gSetField"] = "txt_afwdtannm"
        return FATAL_ERR
    return NOMAL_OK
