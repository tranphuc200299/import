import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context
from main.common.function import SqlExecute
from main.common.function.Const import FATAL_ERR, NOMAL_OK
from main.common.utils import Response

__logger = logging.getLogger(__name__)

PROGID = "cfsm3100"
CFSC31_MODE0 = 0
CFSC31_MODE1 = 1


@update_context()
def f_cfsc3100(request):
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "txt_aszouchicd_Change":
            id_show_data = txt_aszouchicd_Change(request)
            return Response(request).json_response_textchange(id_show_data)
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
    return render(request, "f_cfsc3100.html", request.context)


def Form_Load(request):
    try:
        init_form(request, CFSC31_MODE0)

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
        # TODO
        # OraError("", "")


def txt_aszouchicd_Change(request):
    request.context["txt_aszouchicd"] = request.context["txt_aszouchicd"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_aszouchicd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]

def cmd_search_Click(request):
    try:
        init_form(CFSC31_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql = "SELECT * "
        sql += " FROM TBSZOUCHI" + strProcTbl
        sql += " WHERE SZOUCHICD = " + request.context["txt_aszouchicd"]
        sql += " FOR UPDATE NOWAIT"
        RsTbSZouchi = SqlExecute(sql).all()
        if not RsTbSZouchi.Rows:
            request.context["cmd_entry_enable"] = True
        else:
            # TODO
            request.context["txt_aszouchinm"] = "DbDataChange(RsTbSZouchi.Rows[0], 'SZOUCHINM')"
            request.context["cmd_change_enable"] = True
            request.context["cmd_delete_enable"] = True
        request.context["gSetField"] = "txt_aszouchinm"
    except Exception as e:
        __logger.error(e)
        # TODO
        # OraError("TBSZOUCHI" + strProcTbl, "sql")


def cmd_entry_Click(request):
    try:
        if inpdatachk1(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "INSERT INTO TBSZOUCHI" & strProcTbl & " "
            sql += "(SZOUCHICD,SZOUCHINM,UDATE,UWSID) "
            sql += "VALUES("
            sql += request.context["txt_aszouchicd"] + ","
            sql += request.context["txt_aszouchinm"] + ","
            sql += "CURRENT_TIMESTAMP" + ","
            # TODO
            sql += "iniWsNo" + ")"
            SqlExecute(sql).execute()
        init_form(CFSC31_MODE0)
        request.context["gSetField"] = "txt_aszouchicd"
    except Exception as e:
        __logger.error(e)
        # TODO
        # OraError("TBSZOUCHI" + strProcTbl, "sql")
        request.context["cmd_entry_enable"] = False


def cmd_change_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "UPDATE TBSZOUCHI" + strProcTbl + " "
            sql += "SET SZOUCHINM = " + request.context["txt_aszouchinm"] + ","
            sql += "UDATE = CURRENT_TIMESTAMP" + ","
            sql += "UWSID = iniWsNo" + " "
            sql += "WHERE SZOUCHICD = " + request.context["txt_aszouchicd"]
            SqlExecute(sql).execute()
        init_form(CFSC31_MODE0)
        request.context["gSetField"] = "txt_aszouchicd"
    except Exception as e:
        __logger.error(e)
        # TODO
        # OraError("TBSZOUCHI" + strProcTbl, "sql")
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False


def cmd_delete_Click(request):
    try:
        with transaction.atomic():
            sql = "DELETE FROM TBSZOUCHI" + strProcTbl + " "
            sql += sql + "WHERE SZOUCHICD = " + request.context["txt_aszouchicd"]
            SqlExecute(sql).execute()
        init_form(CFSC31_MODE0)
        request.context["gSetField"] = "txt_aszouchicd"
    except Exception as e:
        __logger.error(e)
        # TODO
        # OraError("TBSZOUCHI" + strProcTbl, "sql")
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False

    init_form(CFSC31_MODE0)
    request.context["gSetField"] = "txt_aszouchicd"


def init_form(request, intMode):
    if intMode == CFSC31_MODE0:
        request.context["txt_aszouchicd"] = ""
    request.context["txt_aszouchinm"] = ""


def inpdatachk1(request):
    if request.context["txt_aszouchicd"] == "":
        request.context["lblMsg"] = "必須入力エラー倉庫内蔵置場所コードを入力して下さい。"
        request.context["gSetField"] = "txt_aszouchicd"
        return FATAL_ERR
    return NOMAL_OK


def inpdatachk2(request):
    if request.context["txt_aszouchinm"] == "":
        request.context["lblMsg"] = "必須入力エラー倉庫内蔵置場所名称を入力して下さい。"
        request.context["gSetField"] = "txt_aszouchinm"
        return FATAL_ERR
    if 20 < len(request.context["txt_aszouchinm"]):
        request.context["lblMsg"] = "入力桁数エラー倉庫内蔵置場所名称は" + "20" + "桁以内で入力して下さい。"
        request.context["gSetField"] = "txt_aszouchinm"
        return FATAL_ERR
    return NOMAL_OK
