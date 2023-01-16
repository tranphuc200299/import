import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute, Common
from main.common.function.Common import dbField, dbField, DbDataChange, IsNumeric
from main.common.function.Const import \
    FATAL_ERR, NOMAL_OK, csSYUBTKBN_1, csSYUBTKBN_2, csFCALC_1, csFCALC_2, csFCALC_3, DB_NOT_FIND
from main.common.function.TableCheck import TbOpe_TableCheck
from main.common.utils import Response

__logger = logging.getLogger(__name__)

PROGID = "cfsm1900"
CFSC19_MODE0 = 0
CFSC19_MODE1 = 1
CFSC19_CONVERT_MIN = 0
CFSC19_CONVERT_MAX = 999
CFSC19_SYUBTKBN_WEIGHT = "重量単位"
CFSC19_SYUBTKBN_MEASURE = "容積単位"


@update_context()
@load_cfs_ini("menu4")
def f_cfsc1900(request):
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
        elif action == "txt_astanicd_Change":
            id_show_data = txt_astanicd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_iconvert_LostFocus":
            id_show_data = txt_iconvert_LostFocus(request)
            return Response(request).json_response_event_js_html(id_show_data)
    else:
        Form_Load(request)
    return render(request, "menu/menu4/f_cfsc1900.html", request.context)


def Form_Load(request):
    try:
        init_form(request, CFSC19_MODE0)
        request.context["cmd_entry_enable"] = False
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
    except Exception as e:
        __logger.error(e)


def init_form(request, intMode):
    if intMode == CFSC19_MODE0:
        request.context["txt_astanicd"] = ""
    request.context["txt_astaninm"] = ""
    request.context["cmb_asyubtkbn"] = "0"
    request.context["txt_iconvert"] = ""
    request.context["txt_iconvert"] = ""


def cmd_search_Click(request):
    try:
        init_form(request, CFSC19_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql = "SELECT * "
        sql += " FROM TBSTANI" + request.cfs_ini["iniUpdTbl"]
        sql += " WHERE STANICD = " + dbField(request.context['txt_astanicd'])
        sql += " FOR UPDATE NOWAIT"
        RsTbSTani = SqlExecute(sql).all()
        if not RsTbSTani.Rows:
            request.context["cmd_entry_enable"] = True
        else:
            request.context["txt_astaninm"] = DbDataChange(RsTbSTani.Rows[0]["staninm"])
            if DbDataChange(RsTbSTani.Rows[0]["syubtkbn"]) == 1:
                request.context["cmb_asyubtkbn"] = "0"
            elif DbDataChange(RsTbSTani.Rows[0]["syubtkbn"]) == 2:
                request.context["cmb_asyubtkbn"] = "1"

            request.context["txt_iconvert"] = DbDataChange(RsTbSTani.Rows[0]["convert"])

            request.context["cmd_change_enable"] = True
            request.context["cmd_delete_enable"] = True
        request.context["gSetField"] = "txt_astaninm"

    except Exception as e:
        __logger.error(e)
        # TODO
        # OraError "TBSFREETM" & strProcTbl, sql


def inpdatachk1(request):
    if not request.context["txt_astanicd"]:
        # TODO
        # MsgDspWarning "必須入力エラー", "オペレータコードを入力して下さい。"
        request.context["gSetField"] = "txt_astanicd"
        return FATAL_ERR
    return NOMAL_OK


def txt_astanicd_Change(request):
    request.context["txt_astanicd"] = request.context["txt_astanicd"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_astanicd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]
def cmd_entry_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "INSERT INTO TBSTANI" + request.cfs_ini["iniUpdTbl"] + ""
            sql += " (STANICD,STANINM,SYUBTKBN,CONVERT,UDATE,UWSID) "
            sql += " VALUES ("
            sql += dbField(request.context["txt_astanicd"]) + ","
            sql += dbField(request.context["txt_astaninm"]) + ","
            if str(request.context["cmb_asyubtkbn"]) == "0":
                sql += dbField("1") + ","
            elif str(request.context["cmb_asyubtkbn"]) == "1":
                sql += dbField("2") + ","
            sql += dbField(request.context['txt_iconvert']) + ","
            sql += "CURRENT_TIMESTAMP" + ","
            sql += dbField(request.cfs_ini["iniWsNo"]) + ")"
            SqlExecute(sql).execute()
            init_form(request, CFSC19_MODE0)
            request.context["gSetField"] = "txt_astanicd"

    except Exception as a:
        __logger.error(a)
        request.context["cmd_entry_enable"] = False

def inpdatachk2(request):
    if request.context["txt_astaninm"] == '':
        # TODO
        # MsgDspWarning "必須入力エラー", "数量単位名称を入力して下さい。"
        request.context["gSetField"] = "txt_astaninm"
        return FATAL_ERR
    if len(request.context["txt_astaninm"]) > 25:
        # TODO
        # MsgDspWarning "入力桁数エラー", "数量単位名称は" & txt_astaninm.MaxLength & "桁以内で入力して下さい。"
        request.context["gSetField"] = "txt_astaninm"
        return FATAL_ERR
    if request.context["txt_iconvert"] == "":
        # TODO
        # MsgDspWarning "必須入力エラー", "換算式を入力して下さい。"
        request.context["gSetField"] = "txt_iconvert"
        return FATAL_ERR
    if not IsNumeric(request.context["txt_iconvert"]):
        # TODO
        # MsgDspWarning "入力整合性エラー", "換算式は整数(ZZ,ZZZ,ZZ9.999形式)で入力して下さい。"
        request.context["gSetField"] = "txt_iconvert"
        return FATAL_ERR
    if CFSC19_CONVERT_MIN > float(request.context["txt_iconvert"]) or CFSC19_CONVERT_MAX < float(
            request.context["txt_iconvert"]):
        # TODO
        # MsgDspWarning "入力整合性エラー", " 換算式は & Format(CDbl(CFSC19_CONVERT_MIN), "#,0.000") & から & Format(CDbl(CFSC19_CONVERT_MAX), "#,0.000") & 以内で入力して下さい。"
        request.context["gSetField"] = "txt_iconvert"
        return FATAL_ERR
    return NOMAL_OK
def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    init_form(request, CFSC19_MODE0)
    request.context["gSetField"] = "txt_astanicd"


def cmd_change_Click(request):
    try:
        sql = "UPDATE TBSTANI" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "SET STANINM = " + dbField(request.context["txt_astaninm"]) + ","
        if str(request.context["cmb_asyubtkbn"]) == "0":
            sql += dbField("1") + ","
        elif str(request.context["cmb_asyubtkbn"]) == "1":
            sql += dbField("2") + ","
        sql += "CONVERT =" + dbField(request.context["txt_iconvert"]) + ","
        sql += " UDATE = CURRENT_TIMESTAMP" + ","
        sql += "UWSID = " + dbField(request.cfs_ini["iniWsNo"]) + " "
        sql += " WHERE STANICD = " + dbField(request.context["txt_astanicd"])
        sql += " AND FREEKBN = " + dbField(request.context["txt_astanicd"])
        SqlExecute(sql).execute()
        init_form(request, CFSC19_MODE0)
        request.context["gSetField"] = "txt_astanicd"
    except Exception as e:
        __logger.error(e)
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False


def cmd_delete_Click(request):
    try:
        with transaction.atomic():
            sql = "DELETE FROM TBSTANI" + request.cfs_ini["iniUpdTbl"] + ""
            sql += " WHERE STANICD = " + dbField(request.context["txt_astanicd"])
            SqlExecute(sql).execute()
        init_form(request, CFSC19_MODE0)
        request.context["gSetField"] = "txt_aopecd"

    except Exception as e:
        __logger.error(e)
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False


def txt_iconvert_LostFocus(request):
    if request.context["txt_iconvert"] == "":
        if not IsNumeric(request.context["txt_iconvert"]):
            # TODO
            # MsgDspWarning "入力整合性エラー", "換算式は整数(ZZ,ZZZ,ZZ9.999形式)で入力して下さい。"
            request.context["gSetField"] = "txt_iconvert"
            return FATAL_ERR
        if CFSC19_CONVERT_MIN > float(request.context["txt_iconvert"]) or CFSC19_CONVERT_MAX < float(
                request.context["txt_iconvert"]):
            # TODO
            # MsgDspWarning "入力整合性エラー", " 換算式は & Format(CDbl(CFSC19_CONVERT_MIN), "#,0.000") & から & Format(CDbl(CFSC19_CONVERT_MAX), "#,0.000") & 以内で入力して下さい。"
            request.context["gSetField"] = "txt_iconvert"
            return FATAL_ERR
        return NOMAL_OK
