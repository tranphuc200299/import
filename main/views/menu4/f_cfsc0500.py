import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute, Common
from main.common.function.Common import sqlStringConvert
from main.common.function.Const import \
    FATAL_ERR, NOMAL_OK, csFKISANKBN_1, csFKISANKBN_2, csFCALC_1, csFCALC_2, csFCALC_3, DB_NOT_FIND
from main.common.function.TableCheck import TbOpe_TableCheck
from main.common.utils import Response

__logger = logging.getLogger(__name__)

PROGID = "cfsm0500"
CFSC05_MODE0 = 0
CFSC05_MODE1 = 1
CFSC05_FDAYS_MIN = 0
CFSC05_FDAYS_MAX = 999


@update_context()
@load_cfs_ini("menu4")
def f_cfsc0500(request):
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "txt_aopecd_Change":
            id_show_data = txt_aopecd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_afreekbn_Change":
            id_show_data = txt_afreekbn_Change(request)
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
    return render(request, "menu/menu4/f_cfsc0500.html", request.context)


def Form_Load(request):
    try:
        init_form(request, CFSC05_MODE0)
        request.context["cmd_entry_enable"] = False
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
    except Exception as e:
        __logger.error(e)


def init_form(request, intMode):
    if intMode == CFSC05_MODE0:
        request.context["txt_aopecd"] = ""
        request.context["txt_afreekbn"] = ""
    request.context["cmb_afksankbn"] = "0"
    request.context["txt_ifdays"] = ""
    request.context["cmb_afcalc"] = "0"


def inpdatachk1(request):
    if request.context["txt_aopecd"] == "":
        request.context["lblMsg"] = "必須入力エラー", "オペレータコードを入力して下さい。"
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR
    intRtn = TbOpe_TableCheck(request.context["txt_aopecd"], request.cfs_ini["iniUpdTbl"])
    if intRtn == DB_NOT_FIND:
        request.context["lblMsg"] = "コード未登録エラー", "Operator Code Tableが登録されていません。"
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR
    elif intRtn == FATAL_ERR:
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR

    return NOMAL_OK


def cmd_search_Click(request):
    try:
        init_form(request, CFSC05_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql = "SELECT * "
        sql += " FROM TBFREETM" + request.cfs_ini["iniUpdTbl"]
        sql += " WHERE OPECD = " + sqlStringConvert(request.context['txt_aopecd'])
        sql += " AND FREEKBN = " + sqlStringConvert(request.context['txt_afreekbn'])
        sql += " FOR UPDATE NOWAIT"
        RsTbFreeTm = SqlExecute(sql).all()
        if len(RsTbFreeTm.Rows) == 0:
            request.context["cmd_entry_enable"] = True
        else:
            if csFKISANKBN_1 == Common.DbDataChange(RsTbFreeTm.Rows[0]["fkisankbn"]):
                request.context["cmb_afksankbn"] = "0"
            elif csFKISANKBN_2 == Common.DbDataChange(RsTbFreeTm.Rows[0]["fkisankbn"]):
                request.context["cmb_afksankbn"] = "1"
            request.context["txt_ifdays"] = Common.DbDataChange(RsTbFreeTm.Rows[0]["fdays"])
            if Common.DbDataChange(RsTbFreeTm.Rows[0]["fkisankbn"]) == csFCALC_1:
                request.context["cmb_afcalc"] = "0"
            elif Common.DbDataChange(RsTbFreeTm.Rows[0]["fkisankbn"]) == csFCALC_2:
                request.context["cmb_afcalc"] = "1"
            elif Common.DbDataChange(RsTbFreeTm.Rows[0]["fkisankbn"]) == csFCALC_3:
                request.context["cmb_afcalc"] = "2"
            request.context["cmd_change"] = True
            request.context["cmd_delete"] = True

        request.context["gSetField"] = "cmb_afksankbn"

    except Exception as e:
        __logger.error(e)
        # TODO
        # OraError "TBSFREETM" & strProcTbl, sql


def inpdatachk2(request):
    if request.context["txt_ifdays"] == "":
        request.context["lblMsg"] = "必須入力エラー", "フリータイム日数を入力して下さい。"
        request.context["gSetField"] = "txt_ifdays"
        return FATAL_ERR
    if not Common.IsNumeric(request.context["txt_ifdays"]):
        request.context["lblMsg"] = "入力整合性エラー", "フリータイム日数は整数(ZZ9形式)で入力して下さい。"
        request.context["gSetField"] = "txt_ifdays"
        return FATAL_ERR
    if CFSC05_FDAYS_MIN > len(request.context["txt_ifdays"]) or CFSC05_FDAYS_MAX < len(request.context["txt_ifdays"]):
        request.context["lblMsg"] = "入力整合性エラー", "フリータイム日数は" + str(CFSC05_FDAYS_MIN) + "から" + str(
            CFSC05_FDAYS_MAX) + "以内で入力して下さい。"
        request.context["gSetField"] = "txt_ifdays"
        return FATAL_ERR
    return NOMAL_OK


def cmd_delete_Click(request):
    try:
        with transaction.atomic():
            sql = "DELETE FROM TBFREETM" + request.cfs_ini["iniUpdTbl"] + ""
            sql += " WHERE OPECD = " + sqlStringConvert(request.context["txt_aopecd"])
            sql += " AND FREEKBN = " + sqlStringConvert(request.context["txt_afreekbn"])
            SqlExecute(sql).execute()
        init_form(request, CFSC05_MODE0)
        request.context["gSetField"] = "txt_aopecd"

    except Exception as e:
        __logger.error(e)
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False


def cmd_change_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "UPDATE TBFREETM" + request.cfs_ini["iniUpdTbl"] + ""
            if request.context["cmb_afksankbn"] == "0":
                sql += " SET FKISANKBN = " + sqlStringConvert("1") + ","
            if request.context["cmb_afksankbn"] == "1":
                sql += " SET FKISANKBN = " + sqlStringConvert("2") + ","
            sql += "FDAYS = " + request.context["txt_ifdays"] + ","
            if request.context["cmb_afcalc"] == "0":
                sql += " FCALC = " + sqlStringConvert("1") + ","
            elif request.context["cmb_afcalc"] == "1":
                sql += " FCALC = " + sqlStringConvert("2") + ","
            elif request.context["cmb_afcalc"] == "2":
                sql += " FCALC = " + sqlStringConvert("3") + ","
            sql += " UDATE = CURRENT_TIMESTAMP" + ","
            sql += "UWSID = " + sqlStringConvert(request.cfs_ini["iniWsNo"]) + " "
            sql += " WHERE OPECD = " + sqlStringConvert(request.context["txt_aopecd"])
            sql += " AND FREEKBN = " + sqlStringConvert(request.context["txt_afreekbn"])
            SqlExecute(sql).execute()
            init_form(request, CFSC05_MODE0)
            request.context["gSetField"] = "txt_aopecd"
    except Exception as e:
        __logger.error(e)
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False


def cmd_entry_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "INSERT INTO TBFREETM" + request.cfs_ini["iniUpdTbl"] + ""
            sql += " (OPECD,FREEKBN,FKISANKBN,FDAYS,FCALC,UDATE,UWSID) "
            sql += " VALUES ("
            sql += sqlStringConvert(request.context["txt_aopecd"]) + ","
            sql += sqlStringConvert(request.context["txt_afreekbn"]) + ","
            if str(request.context["cmb_afksankbn"]) == "0":
                sql += sqlStringConvert("1") + ","
            elif str(request.context["cmb_afksankbn"]) == "1":
                sql += sqlStringConvert("2") + ","
            sql += sqlStringConvert(request.context['txt_ifdays']) + ","
            if request.context["cmb_afcalc"] == "0":
                sql += sqlStringConvert("1") + ","
            elif request.context["cmb_afcalc"] == "1":
                sql += sqlStringConvert("2") + ","
            elif request.context["cmb_afcalc"] == "2":
                sql += sqlStringConvert("3") + ","
            sql += "CURRENT_TIMESTAMP" + ","
            sql += sqlStringConvert(request.cfs_ini["iniWsNo"]) + ")"
            SqlExecute(sql).execute()
            init_form(request, CFSC05_MODE0)
            request.context["gSetField"] = "txt_aopecd"

    except Exception as a:
        __logger.error(a)
        request.context["cmd_entry_enable"] = False


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    init_form(request, CFSC05_MODE0)
    request.context["gSetField"] = "txt_aopecd"


def txt_aopecd_Change(request):
    request.context["txt_aopecd"] = request.context["txt_aopecd"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_aopecd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def txt_afreekbn_Change(request):
    request.context["txt_afreekbn"] = request.context["txt_afreekbn"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_afreekbn", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]
