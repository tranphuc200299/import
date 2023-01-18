import logging
from django.db import transaction
from django.shortcuts import render
from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute, Const, Common
from main.common.function.Common import dbField, DbDataChange
from main.common.function.Const import NOMAL_OK, FATAL_ERR, csTAXKBN_0, csTAXKBN_1, csTAXKBN_2
from main.common.function.DspMessage import MsgDspError
from main.common.utils import Response
from main.middleware.exception.exceptions import PostgresException

PROGID = "cfsm2300"
CFSC23_MODE0 = 0
CFSC23_MODE1 = 1
CFSC23_TANKA_MIN = 0
CFSC23_TANKA_MAX = 99999999

__logger = logging.getLogger(__name__)


@update_context()
@load_cfs_ini("menu4")
def f_cfsc2300(request):
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
        elif action == "txt_azworkcd_Change":
            id_show_data = txt_azworkcd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_itanka_LostFocus":
            id_show_data = txt_itanka_LostFocus(request)
            return Response(request).json_response_event_js_html(id_show_data)
    else:
        Form_Load(request)
    return render(request, "menu/menu4/f_cfsc2300.html", request.context)


def init_form(request, intMode):
    if intMode == CFSC23_MODE0:
        request.context["txt_azworkcd"] = ""

    request.context["txt_azworknm"] = ""
    request.context["txt_itanka"] = ""
    request.context["cmb_ataxkbn"] = "0"
    request.context["txt_akaisu"] = ""


def inpdatachk1(request):
    if request.context["txt_azworkcd"] == "":
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "雑作業コードを入力して下さい。")
        request.context["gSetField"] = "txt_azworkcd"
        return FATAL_ERR
    return NOMAL_OK


def inpdatachk2(request):
    if request.context["txt_azworknm"] == '':
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "雑作業名称を入力して下さい。")
        request.context["gSetField"] = "txt_azworknm"
        return FATAL_ERR
    if len(request.context["txt_azworknm"]) > 25:
        MsgDspError(request, Const.MSG_DSP_WARN, "入力桁数エラー", "雑作業名称は" + "25" + "桁以内で入力して下さい。")
        request.context["gSetField"] = "txt_azworknm"
        return FATAL_ERR
    if request.context["txt_itanka"] == '':
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "単価を入力して下さい。")
        request.context["gSetField"] = "txt_itanka"
        return FATAL_ERR
    if not Common.IsNumeric(request.context["txt_itanka"]):
        MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー", "単価は整数(\ZZ,ZZZ,ZZ9形式)で入力して下さい。")
        request.context["gSetField"] = "txt_itanka"
        return FATAL_ERR
    if CFSC23_TANKA_MIN > float(request.context["txt_itanka"].replace(',', '')) or CFSC23_TANKA_MAX < float(
            request.context["txt_itanka"].replace(',', '')):
        MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー",
                    "名古屋用加算単価は" + f"{CFSC23_TANKA_MIN :,}" + "から" + f"{CFSC23_TANKA_MAX :,}" + "以内で入力して下さい。")
        request.context["gSetField"] = "txt_itanka"
        return FATAL_ERR

    request.context["txt_itanka"] = int(request.context['txt_itanka'].replace(',', ''))
    return NOMAL_OK


def Form_Load(request):
    init_form(request, CFSC23_MODE0)
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"


def cmd_search_Click(request):
    sql = ""
    try:
        init_form(request, CFSC23_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql += "SELECT * "
        sql += "FROM TBZWORK" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "WHERE ZWORKCD = " + dbField(request.context["txt_azworkcd"])
        sql += " FOR UPDATE NOWAIT"
        RsTbZWork = SqlExecute(sql).all()
        if len(RsTbZWork.Rows) == 0:
            request.context["cmd_entry_enable"] = "True"
        else:
            request.context["txt_azworknm"] = DbDataChange(RsTbZWork.Rows[0]["zworknm"])
            if DbDataChange((RsTbZWork.Rows[0]["tanka"])):
                request.context["txt_itanka"] = f'{DbDataChange(RsTbZWork.Rows[0]["tanka"]):,}'
            else:
                request.context["txt_itanka"] = 0
            if DbDataChange(RsTbZWork.Rows[0]["taxkbn"]) == "0":
                request.context["cmb_ataxkbn"] = "0"
            elif DbDataChange(RsTbZWork.Rows[0]["taxkbn"]) == "1":
                request.context["cmb_ataxkbn"] = "1"
            elif DbDataChange(RsTbZWork.Rows[0]["taxkbn"]) == "2":
                request.context["cmb_ataxkbn"] = "2"
            request.context["txt_akaisu"] = DbDataChange(RsTbZWork.Rows[0]["kaisu"])
            request.context["cmd_change_enable"] = "True"
            request.context["cmd_delete_enable"] = "True"
        request.context["gSetField"] = "txt_azworknm"

    except Exception as e:
        raise PostgresException(Error=e, DbTbl="TBZWORK" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_entry_Click(request):
    sql = ""
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        sql += "INSERT INTO TBZWORK" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "(ZWORKCD,ZWORKNM,TANKA,TAXKBN,KAISU,UDATE,UWSID) "
        sql += "VALUES("
        sql += dbField(request.context["txt_azworkcd"]) + ","
        sql += dbField(request.context["txt_azworknm"]) + ","
        sql += f"{request.context['txt_itanka']}" + ","
        if request.context["cmb_ataxkbn"] == "0":
            sql += dbField(csTAXKBN_0) + ","
        elif request.context["cmb_ataxkbn"] == "1":
            sql += dbField(csTAXKBN_1) + ","
        elif request.context["cmb_ataxkbn"] == "2":
            sql += dbField(csTAXKBN_2) + ","
        sql += dbField(request.context["txt_akaisu"]) + ","
        sql += 'CURRENT_TIMESTAMP' + ","
        sql += dbField(request.cfs_ini["iniWsNo"]) + ')'
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC23_MODE0)
        request.context["gSetField"] = "txt_azworkcd"
    except Exception as e:
        request.context["cmd_entry_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBZWORK" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_change_Click(request):
    if inpdatachk2(request) != NOMAL_OK:
        return
    sql = ""
    sql += "UPDATE TBZWORK" + request.cfs_ini["iniUpdTbl"] + " "
    sql += "SET ZWORKNM = " + dbField(request.context["txt_azworknm"]) + ","
    sql += f"TANKA =  {request.context['txt_itanka']},"
    if request.context["cmb_ataxkbn"] == "0":
        sql += "TAXKBN = " + dbField(csTAXKBN_0) + ","
    elif request.context["cmb_ataxkbn"] == "1":
        sql += "TAXKBN = " + dbField(csTAXKBN_1) + ","
    elif request.context["cmb_ataxkbn"] == "2":
        sql += "TAXKBN = " + dbField(csTAXKBN_2) + ","
    sql += "KAISU = " + dbField(request.context["txt_akaisu"]) + ","
    sql += "UDATE = CURRENT_TIMESTAMP" + ","
    sql += "UWSID = " + dbField(request.cfs_ini["iniWsNo"]) + " "
    sql += "WHERE ZWORKCD = " + dbField(request.context["txt_azworkcd"])
    try:
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC23_MODE0)
        request.context["gSetField"] = "txt_azworkcd"
    except Exception as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="ZWORKNM" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"

    init_form(request, CFSC23_MODE0)
    request.context["gSetField"] = "txt_azworkcd"


def cmd_delete_Click(request):
    sql = ""
    sql += "DELETE FROM TBZWORK" + request.cfs_ini["iniUpdTbl"] + " "
    sql += 'WHERE ZWORKCD = ' + dbField(request.context["txt_azworkcd"])
    try:
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC23_MODE0)
        request.context["gSetField"] = "txt_azworkcd"
    except Exception as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBZWORK" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def txt_azworkcd_Change(request):
    request.context["txt_azworkcd"] = request.context["txt_azworkcd"].upper()
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"
    return ["txt_azworkcd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def txt_itanka_LostFocus(request):
    if request.context["txt_itanka"]:
        if not Common.IsNumeric(request.context["txt_itanka"]):
            MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー", "単価は整数(\ZZ,ZZZ,ZZ9形式)で入力して下さい。")
            request.context["gSetField"] = "txt_itanka"
        if CFSC23_TANKA_MIN > float(request.context["txt_itanka"].replace(',', '')) or CFSC23_TANKA_MAX < float(
                request.context["txt_itanka"].replace(',', '')):
            MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー",
                        "単価は" + f"{CFSC23_TANKA_MIN:,}" + "から" + f"{CFSC23_TANKA_MAX:,}" + "以内で入力して下さい。")
            request.context["gSetField"] = "txt_itanka"
            return "txt_itanka"
        request.context["txt_itanka"] = f"{int(request.context['txt_itanka'].replace(',', '')):,}"
    return "txt_itanka"
