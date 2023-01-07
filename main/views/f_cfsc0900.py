import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context
from main.common.function import SqlExecute
from main.common.function.Const import FATAL_ERR, NOMAL_OK
from main.common.utils import Response

__logger = logging.getLogger(__name__)

PROGID = "cfsm0900"
CFSC09_MODE0 = 0
CFSC09_MODE1 = 1


@update_context()
def f_cfsc0900(request):
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "cmd_change_Click":
            cmd_change_Click(request)
        if action == "cmd_delete_Click":
            cmd_delete_Click(request)
        if action == "cmd_entry_Click":
            cmd_entry_Click(request)
        if action == "cmd_search_Click":
            cmd_search_Click(request)
        if action == "cmd_cancel_Click":
            cmd_cancel_Click(request)
    return render(request, 'f_cfsc0900.html', request.context)


def Form_Load(request):
    try:
        init_form(request, CFSC09_MODE0)
        request.context["cmd_entry_enable"] = False
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        request.context["lbl_aSelHozNam"] = request.GET["strSelHozNam"]
        global strProcHozCd, strProcHozNam, strProcTbl
        strProcHozCd = request.GET["strSelHozCd"]
        strProcHozNam = request.GET["strSelHozNam"]
        strProcTbl = request.GET["strSelTbl"]
    except Exception as e:
        __logger.error(e)


def init_form(request, intMode):
    if intMode == CFSC09_MODE0:
        request.context["txt_aportcd"] = ""
    request.context["txt_aportnm"] = ""
    request.context["txt_aareacd"] = ""


def inpdatachk1(request):
    if request.context["txt_aportcd"] == "":
        request.context["lblMsg"] = "必須入力エラー", "ポートコードを入力して下さい。"
        request.context["gSetField"] = "txt_aportcd"
    return FATAL_ERR


def inpdatachk2(request):
    if request.context["txt_aportnm"] == "":
        request.context["lblMsg"] = "必須入力エラー", "ポート名称を入力して下さい。"
        request.context["gSetField"] = "txt_aportnm"
        return FATAL_ERR
    if request.context["txt_aportnm"] < str(len(request.context["txt_aportnm"])):
        request.context["lblMsg"] = "入力桁数エラー ", "ポート名称は", "桁以内で入力して下さい。"
        request.context["gSetField"] = "txt_aportnm"
        return FATAL_ERR
    return NOMAL_OK


def cmd_change_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "UPDATE TBPORT" + strProcTbl + ""
            sql += sql + "SET PORTNM = " + request.context["txt_aportnm"] + ","
            sql += sql + "AREACD = " + request.context["txt_aareacd"] + ","
            sql += sql + "CURRENT_TIMESTAMP" + ","
            sql += sql + "UWSID = " + "iniWsNo" + ")"
            sql += "WHERE PORTCD = " + request.context["txt_aportcd"]
            SqlExecute(sql).execute()
        init_form(request, CFSC09_MODE0)
        request.context["gSetField"] = "txt_aportcd"
    except Exception as e:
        __logger.error(e)
        request.context["cmd_entry_enable"] = False
        request.context["cmd_delete_enable"] = False


def cmd_delete_Click(request):
    try:
        with transaction.atomic():
            sql = "DELETE FROM TBPORT" + strProcTbl + ""
            sql += sql + "WHERE PORTCD = " + request.context["txt_aportcd"]
            SqlExecute(sql).execute()
        init_form(request, CFSC09_MODE0)
        request.context["gSetField"] = "txt_aportcd"
    except Exception as e:
        __logger.error(e)
        # TODO
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False


def cmd_entry_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "INSERT INTO TBPORT" + strProcTbl + ""
            sql += sql + "(PORTCD,PORTNM,AREACD,UDATE,UWSID) "
            sql += sql + "VALUES("
            sql += sql + request.context["txt_aportcd"] + ","
            sql += sql + request.context["txt_aportnm"] + ","
            sql += sql + request.context["txt_aareacd"] + ","
            sql += sql + "CURRENT_TIMESTAMP" + ","
            sql += "iniWsNo" + ")"
            SqlExecute(sql).execute()
        init_form(request, CFSC09_MODE0)
        request.context["gSetField"] = "txt_aportcd"
    except Exception as e:
        __logger.error(e)
        request.context["cmd_entry_enable"] = False


def cmd_search_Click(request):
    try:
        init_form(request, CFSC09_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql = "SELECT * "
        sql += sql + "FROM TBPORT " + strProcTbl + ""
        sql += sql + "WHERE PORTCD = " + request.context["txt_aportcd"]
        sql += sql + "FOR UPDATE NOWAIT"
        RsTbPort = SqlExecute(sql).all()
        if len(RsTbPort) == 0:
            request.context["cmd_entry_enable"] = True
        else:
            # TODO
            request.context["txt_aportnm"] = "DbDataChange(RsTbPort.Rows[0], 'PORTNM')"
            request.context["txt_aareacd"] = "DbDataChange(RsTbPort.Rows[0], 'AreaCd')"
            request.context["cmd_change_enable"] = True
            request.context["cmd_delete_enable"] = True

        request.context["gSetField"] = "txt_aportnm"
    except Exception as e:
        __logger.error(e)


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    init_form(request, CFSC09_MODE0)
    request.context["gSetField"] = "txt_aportcd"
