import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context
from main.common.function import SqlExecute, Common
from main.common.function.Const import \
    FATAL_ERR, NOMAL_OK, csFKISANKBN_1, csFKISANKBN_2, csFCALC_1, csFCALC_2, csFCALC_3
from main.common.utils import Response

__logger = logging.getLogger(__name__)

PROGID = "cfsm0500"
CFSC05_MODE0 = 0
CFSC05_MODE1 = 1

CFSC05_FKISANKBN_TYPE1 = "搬入日起算"
CFSC05_FKISANKBN_TYPE2 = "搬入日翌日起算"
CFSC05_FCALC_TYPE1 = "日祝除く"
CFSC05_FCALC_TYPE2 = "土日祝除く"
CFSC05_FCALC_TYPE3 = "全て含む"
CFSC05_FDAYS_MIN = 0
CFSC05_FDAYS_MAX = 999


@update_context()
def f_cfsc0500(request):
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "txt_aszouchicd_Change":
            id_show_data = txt_aopecd_Change(request)
            return Response(request).json_response_textchange(id_show_data)
        elif action == "txt_afreekbn_Change":
            id_show_data = txt_afreekbn_Change(request)
            return Response(request).json_response_textchange(id_show_data)
        elif action == "cmd_search":
            cmd_search_Click(request)
        elif action == "cmd_entry_Click":
            cmd_entry_Click(request)
        elif action == "cmd_delete_Click":
            cmd_delete_Click(request)
        elif action == "cmd_cancel_Click":
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
        request.context["lbl_aSelHozNam"] = request.GET["strProcHozNam"]
        global strProcHozCd, strProcHozNam, strProcTbl
        strProcHozCd = request.context["strProcHozCd"]
        strProcHozNam = request.context["strProcHozNam"]
        strProcTbl = request.context["strProcTbl"]
    except Exception as e:
        __logger.error(e)


def init_form(request, intMode):
    if intMode == CFSC05_MODE0:
        request.context["txt_aopecd"] = ""
        request.context["txt_afreekbn"] = ""
    request.context["cmb_afksankbn"] = request.context["cmb_afksankbn"]
    request.context["txt_ifdays"] = ""
    request.context["cmb_afcalc"] = request.context["cmb_afcalc"]


def inpdatachk1(request):
    if request.context["txt_aopecd"] == "":
        request.context["lblMsg"] = "必須入力エラー", "オペレータコードを入力して下さい。"
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR
    return NOMAL_OK


def DbDataChange(DbStr):
    if not DbStr:
        fn_return_value = ''
    else:
        fn_return_value = DbStr
    return fn_return_value


def cmd_search_Click(request):
    try:
        init_form(request, CFSC05_MODE1)
        sql = "SELECT * "
        sql += " FROM TBFREETM " + strProcTbl
        sql += " WHERE OPECD = " + request.context['txt_aopecd']
        sql += " AND FREEKBN = " + request.context['txt_afreekbn']
        sql += "FOR UPDATE NOWAIT"
        RsTbFreeTm = SqlExecute(sql).all()
        if len(RsTbFreeTm) == 0:
            request.context["cmd_entry_enable"] = True
        else:
            if csFKISANKBN_1 == DbDataChange(RsTbFreeTm.Rows[0]["FKISANKBN"]):
                request.context["cmb_afksankbn"] = request.context["cmb_afksankbn"][0]
            elif csFKISANKBN_2 == DbDataChange(RsTbFreeTm.Rows[0]["FKISANKBN"]):
                request.context["cmb_afksankbn"] = request.context["cmb_afksankbn"][1]

            if DbDataChange(RsTbFreeTm.Rows[0]["FKISANKBN"]) == csFCALC_1:
                request.context["cmb_afcalc"] = request.context["cmb_afcalc"][0]
            if DbDataChange(RsTbFreeTm.Rows[0]["FKISANKBN"]) == csFCALC_2:
                request.context["cmb_afcalc"] = request.context["cmb_afcalc"][1]
            if DbDataChange(RsTbFreeTm.Rows[0]["FKISANKBN"]) == csFCALC_3:
                request.context["cmb_afcalc"] = request.context["cmb_afcalc"][2]
            request.context["cmd_change"] = True
            request.context["cmd_delete"] = True
            request.context["txt_ifdays"] = DbDataChange(RsTbFreeTm[0]["FDAYS"])
        request.context["gSetField"] = "txt_aszouchinm"



    except Exception as e:
        __logger.error(e)
        # TODO
        # OraError("TBSZOUCHI" + strProcTbl, "sql")


def inpdatachk2(request):
    if request.context["txt_ifdays"] == "":
        request.context["lblMsg"] = "必須入力エラー", "フリータイム日数を入力して下さい。"
        request.context["gSetField"] = "txt_ifdays"
        return FATAL_ERR
    if Common.IsNumeric(request.context["txt_ifdays"]):
        request.context["lblMsg"] = "入力整合性エラー", "フリータイム日数は整数(ZZ9形式)で入力して下さい。"
        request.context["gSetField"] = "txt_ifdays"
        return FATAL_ERR
    if CFSC05_FDAYS_MIN > len(request.context["txt_ifdays"]) or CFSC05_FDAYS_MAX < len(request.context["txt_ifdays"]):
        request.context["lblMsg"] = "入力整合性エラー", "フリータイム日数は から 以内で入力して下さい。"
        request.context["gSetField"] = "txt_ifdays"
        return FATAL_ERR
    return NOMAL_OK


def cmd_delete_Click(request):
    try:
        with transaction.atomic():
            sql = "DELETE FROM TBFREETM" + strProcTbl + ""
            sql += sql + "WHERE OPECD = " + request.context["txt_aopecd"]
            sql += sql + "AND FREEKBN = " + request.context["txt_afreekbn"]
        init_form(request, CFSC05_MODE0)
        request.context["gSetField"] = "txt_aopecd"
    except Exception as e:
        __logger.error(e)
        # TODO
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False


def cmd_change_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "UPDATE TBFREETM" + strProcTbl + ""
            if request.context["cmb_afksankbn"] == CFSC05_FCALC_TYPE1:
                sql += sql + "SET FKISANKBN = " + csFKISANKBN_1 + ","
            if request.context["cmb_afksankbn"] == CFSC05_FCALC_TYPE2:
                sql += sql + "SET FKISANKBN = " + csFKISANKBN_2 + ","
            sql += sql + "FDAYS = " + request.context["txt_ifdays"] + ","
            if request.context["cmb_afcalc"] == CFSC05_FCALC_TYPE1:
                sql += sql + "FCALC = " + csFCALC_1 + ","
            elif request.context["cmb_afcalc"] == CFSC05_FCALC_TYPE2:
                sql += sql + "FCALC = " + csFCALC_2 + ","
            elif request.context["cmb_afcalc"] == CFSC05_FCALC_TYPE3:
                sql += sql + "FCALC = " + csFCALC_3 + ","
            sql += sql + " UPDATE = CURRENT_TIMESTAMP" + ","
            sql += sql + " UWSID = " + "iniWsNo" + ")"
            sql += sql + " WHERE OPECD = " + request.context["txt_aopecd"]
            sql += sql + " AND FREEKBN = " + request.context["txt_afreekbn"]
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
            sql = "INSERT INTO TBFREETM" + strProcTbl
            sql += sql + "(OPECD,FREEKBN,FKISANKBN,FDAYS,FCALC,UDATE,UWSID)"
            sql += sql + "VALUES("
            sql += sql + request.context["txt_aopecd"] + ","
            sql += sql + request.context["txt_afreekbn"] + ","
            if request.context["cmb_afksankbn"] == CFSC05_FKISANKBN_TYPE1:
                sql += sql + csFKISANKBN_1 + ","
            if request.context["cmb_afksankbn"] == CFSC05_FKISANKBN_TYPE2:
                sql += sql + csFKISANKBN_2 + ","
            sql += sql + request.context['txt_ifdays'] + ","
            if request.context["cmb_afcalc"] == CFSC05_FCALC_TYPE1:
                sql += sql + csFCALC_1 + ","
            if request.context["cmb_afcalc"] == CFSC05_FCALC_TYPE2:
                sql += sql + csFCALC_2 + ","
            if request.context["cmb_afcalc"] == CFSC05_FCALC_TYPE3:
                sql += sql + csFCALC_3 + ","
            sql += sql + "CURRENT_TIMESTAMP" + ","
            sql += "iniWsNo" + ")"
            SqlExecute(sql).execute()
        init_form(request, CFSC05_MODE0)
        request.context["gSetField"] = "txt_aopecd"

    except Exception as a:
        __logger.error(a)


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
