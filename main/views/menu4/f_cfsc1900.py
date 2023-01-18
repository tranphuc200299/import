import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute, Common, Const
from main.common.function.Common import dbField, DbDataChange, IsNumeric
from main.common.function.Const import \
    FATAL_ERR, NOMAL_OK, csSYUBTKBN_1, csSYUBTKBN_2
from main.common.function.DspMessage import MsgDspError
from main.common.utils import Response
from main.middleware.exception.exceptions import PostgresException

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
    init_form(request, CFSC19_MODE0)
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"


def init_form(request, intMode):
    if intMode == CFSC19_MODE0:
        request.context["txt_astanicd"] = ""
    request.context["txt_astaninm"] = ""
    request.context["cmb_asyubtkbn"] = "0"
    request.context["txt_iconvert"] = ""


def cmd_search_Click(request):
    sql = ""
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
            request.context["cmd_entry_enable"] = "True"
        else:
            request.context["txt_astaninm"] = DbDataChange(RsTbSTani.Rows[0]["staninm"])
            if csSYUBTKBN_1 == Common.DbDataChange(RsTbSTani.Rows[0]["syubtkbn"]):
                request.context["cmb_asyubtkbn"] = "0"
            elif csSYUBTKBN_2 == Common.DbDataChange(RsTbSTani.Rows[0]["syubtkbn"]):
                request.context["cmb_asyubtkbn"] = "1"
            request.context["txt_iconvert"] = f'{DbDataChange(RsTbSTani.Rows[0]["convert"]):,.3f}'
            request.context["cmd_change_enable"] = "True"
            request.context["cmd_delete_enable"] = "True"
        request.context["gSetField"] = "txt_astaninm"

    except Exception as e:
        raise PostgresException(Error=e, DbTbl="TBSTANI" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def inpdatachk1(request):
    if request.context["txt_astanicd"] == "":
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "数量単位コードを入力して下さい。")
        request.context["gSetField"] = "txt_astanicd"
        return FATAL_ERR
    return NOMAL_OK


def txt_astanicd_Change(request):
    request.context["txt_astanicd"] = request.context["txt_astanicd"].upper()
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"
    return ["txt_astanicd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def cmd_entry_Click(request):
    sql = ""
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql = "INSERT INTO TBSTANI" + request.cfs_ini["iniUpdTbl"] + ""
            sql += " (STANICD,STANINM,SYUBTKBN,CONVERT,UDATE,UWSID) "
            sql += " VALUES ("
            sql += dbField(request.context["txt_astanicd"]) + ","
            sql += dbField(request.context["txt_astaninm"]) + ","
            if request.context["cmb_asyubtkbn"] == "0":
                sql += dbField(csSYUBTKBN_1) + ","
            elif request.context["cmb_asyubtkbn"] == "1":
                sql += dbField(csSYUBTKBN_2) + ","
            sql += dbField(request.context['txt_iconvert']) + ","
            sql += "CURRENT_TIMESTAMP" + ","
            sql += dbField(request.cfs_ini["iniWsNo"]) + ")"
            SqlExecute(sql).execute()
        init_form(request, CFSC19_MODE0)
        request.context["gSetField"] = "txt_astanicd"
    except Exception as e:
        request.context["cmd_entry_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBSTANI" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def inpdatachk2(request):
    if request.context["txt_astaninm"] == "":
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "数量単位名称を入力して下さい。")
        request.context["gSetField"] = "txt_astaninm"
        return FATAL_ERR
    if len(request.context["txt_astaninm"]) > 25:
        MsgDspError(request, Const.MSG_DSP_WARN, "入力桁数エラー", "数量単位名称は" + str(25) + "桁以内で入力して下さい。")
        request.context["gSetField"] = "txt_astaninm"
        return FATAL_ERR
    if request.context["txt_iconvert"] == "":
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "換算式を入力して下さい。")
        request.context["gSetField"] = "txt_iconvert"
        return FATAL_ERR
    if not IsNumeric(request.context["txt_iconvert"]):
        MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー", "換算式は整数(ZZ,ZZZ,ZZ9.999形式)で入力して下さい。")
        request.context["gSetField"] = "txt_iconvert"
        return FATAL_ERR
    if CFSC19_CONVERT_MIN > float(request.context["txt_iconvert"]) or CFSC19_CONVERT_MAX < float(request.context["txt_iconvert"]):
        MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー",
                    "換算式は" + str(CFSC19_CONVERT_MIN) + str(CFSC19_CONVERT_MAX) + "以内で入力して下さい。")
        request.context["gSetField"] = "txt_iconvert"
        return FATAL_ERR
    return NOMAL_OK

def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"
    init_form(request, CFSC19_MODE0)
    request.context["gSetField"] = "txt_astanicd"


def cmd_change_Click(request):
    sql = ""
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        with transaction.atomic():
            sql += "UPDATE TBSTANI" + request.cfs_ini["iniUpdTbl"] + " "
            sql += "SET STANINM = " + dbField(request.context["txt_astaninm"]) + ","
            if request.context["cmb_asyubtkbn"] == "0":
                sql += " SYUBTKBN = " + dbField(csSYUBTKBN_1) + ","
            elif request.context["cmb_asyubtkbn"] == "1":
                sql += " SYUBTKBN = " + dbField(csSYUBTKBN_2) + ","
            sql += "CONVERT =" + dbField(request.context["txt_iconvert"]) + ","
            sql += " UDATE = CURRENT_TIMESTAMP" + ","
            sql += "UWSID = " + dbField(request.cfs_ini["iniWsNo"]) + " "
            sql += " WHERE STANICD = " + dbField(request.context["txt_astanicd"])
            SqlExecute(sql).execute()
        init_form(request, CFSC19_MODE0)
        request.context["gSetField"] = "txt_astanicd"
    except Exception as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBSTANI" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_delete_Click(request):
    sql = ""
    try:
        with transaction.atomic():
            sql += "DELETE FROM TBSTANI" + request.cfs_ini["iniUpdTbl"] + " "
            sql += "WHERE STANICD = " + dbField(request.context["txt_astanicd"])
            SqlExecute(sql).execute()
        init_form(request, CFSC19_MODE0)
        request.context["gSetField"] = "txt_astanicd"

    except Exception as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise PostgresException(Error=e, DbTbl="TBSTANI" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)

def txt_iconvert_LostFocus(request):
    if request.context["txt_iconvert"]:
        if not IsNumeric(request.context["txt_iconvert"]):
            MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー", "換算式は整数(ZZ,ZZZ,ZZ9.999形式)で入力して下さい。")
            request.context["gSetField"] = "txt_iconvert"
        if CFSC19_CONVERT_MIN > float(request.context["txt_iconvert"].replace(',', '')) or CFSC19_CONVERT_MAX < float(request.context["txt_iconvert"].replace(',', '')):
            MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー", "換算式は" + format(CFSC19_CONVERT_MIN) + "から" + format(CFSC19_CONVERT_MAX) + "以内で入力して下さい。")
            request.context["gSetField"] = "txt_iconvert"
            return FATAL_ERR
        request.context["txt_iconvert"] = f"{float(request.context['txt_iconvert'].replace(',', '')):,.3f}"
        return NOMAL_OK
