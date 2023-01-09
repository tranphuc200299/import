import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute
from main.common.function.Common import DbDataChange, sqlStringConvert
from main.common.function.Const import NOMAL_OK, FATAL_ERR, DB_NOT_FIND, DB_FATAL_ERR
from main.common.function.TableCheck import TbOpe_TableCheck, TbPort_TableCheck
from main.common.utils import Response

__logger = logging.getLogger(__name__)

PROGID = "cfsm0100"
CFSC01_MODE0 = 0
CFSC01_MODE1 = 1


@update_context()
@load_cfs_ini("menu4")
def f_cfsc0100(request):
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
        elif action == "txt_avesselcd_Change":
            id_show_data = txt_avesselcd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_aopecd_Change":
            id_show_data = txt_aopecd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_alportcd_Change":
            id_show_data = txt_alportcd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_aopecd_LostFocus":
            id_show_data = txt_aopecd_LostFocus(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_alportcd_LostFocus":
            id_show_data = txt_alportcd_LostFocus(request)
            return Response(request).json_response_event_js_html(id_show_data)
    else:
        Form_Load(request)
    return render(request, "menu/menu4/f_cfsc0100.html", request.context)


def Form_Load(request):
    init_form(request, CFSC01_MODE0)
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False


def txt_aopecd_LostFocus(request):
    RsTbOpe = Cm_TbOpeChk(request, request.context["txt_aopecd"])
    if not RsTbOpe.Rows:
        # TODO
        # MsgDspWarning "コード未登録エラー", "Operator Code Tableが存在しません。"
        request.context["gSetField"] = "txt_aopecd"
        return request.context["gSetField"]
    else:
        request.context["lbl_aopenm"] = DbDataChange(RsTbOpe.Rows[0]["openm"])
        return request.context["lbl_aopenm"]


def txt_alportcd_LostFocus(request):
    RsTbPort = Cm_TbPortChk(request, request.context["txt_alportcd"])
    if not RsTbPort.Rows:
        # TODO
        # MsgDspWarning "コード未登録エラー", "Port Code Tableが存在しません。"
        request.context["gSetField"] = "txt_alportcd"
        return request.context["gSetField"]
    else:
        request.context["lbl_aportnm"] = DbDataChange(RsTbPort.Rows[0]["portnm"])
        return request.context["lbl_aportnm"]


def txt_avesselcd_Change(request):
    request.context["txt_avesselcd"] = request.context["txt_avesselcd"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_avesselcd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def txt_aopecd_Change(request):
    request.context["txt_aopecd"] = request.context["txt_aopecd"].upper()
    return "txt_aopecd"


def txt_alportcd_Change(request):
    request.context["txt_alportcd"] = request.context["txt_alportcd"].upper()
    return "txt_alportcd"


def cmd_search_Click(request):
    try:
        init_form(request, CFSC01_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql = "SELECT * "
        sql += "FROM TBVESSEL" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "WHERE VESSELCD = " + sqlStringConvert(request.context["txt_avesselcd"])
        sql += " FOR UPDATE NOWAIT"

        RsTbVessel = SqlExecute(sql).all()
        if not RsTbVessel.Rows:
            request.context["cmd_entry_enable"] = True
        else:
            request.context["txt_avesselnm"] = DbDataChange(RsTbVessel.Rows[0]["vesselnm"])
            request.context["txt_acallsign"] = DbDataChange(RsTbVessel.Rows[0]["callsign"])
            request.context["txt_aopecd"] = DbDataChange(RsTbVessel.Rows[0]["opecd"])
            RsTbOpe = Cm_TbOpeChk(request, request.context["txt_aopecd"])
            if RsTbOpe.Rows:
                request.context["lbl_aopenm"] = DbDataChange(RsTbOpe.Rows[0]["openm"])
            request.context["txt_alportcd"] = DbDataChange(RsTbVessel.Rows[0]["lportcd"])
            RsTbPort = Cm_TbPortChk(request, request.context["txt_alportcd"])
            if RsTbPort.Rows:
                request.context["lbl_aportnm"] = DbDataChange(RsTbPort.Rows[0]["portnm"])
            request.context["txt_aberthnm"] = DbDataChange(RsTbVessel.Rows[0]["berthnm"])
            request.context["txt_aline"] = DbDataChange(RsTbVessel.Rows[0]["line"])
            request.context["cmd_change_enable"] = True
            request.context["cmd_delete_enable"] = True
        request.context["gSetField"] = "txt_avesselnm"
    except Exception as e:
        __logger.error(e)
        raise Exception(e)
        # TODO
        # OraError "TBVESSEL" & strProcTbl, sql


def cmd_entry_Click(request):
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return

        sql = "INSERT INTO TBVESSEL" + request.cfs_ini["iniUpdTbl"] + ' '
        sql += "(VESSELCD,VESSELNM,CALLSIGN,OPECD,LPORTCD,BERTHNM,LINE,UDATE,UWSID) "
        sql += 'VALUES('
        sql += sqlStringConvert(request.context["txt_avesselcd"]) + ","
        sql += sqlStringConvert(request.context["txt_avesselnm"]) + ","
        sql += sqlStringConvert(request.context["txt_acallsign"]) + ","
        sql += sqlStringConvert(request.context["txt_aopecd"]) + ","
        sql += sqlStringConvert(request.context["txt_alportcd"]) + ","
        sql += sqlStringConvert(request.context["txt_aberthnm"]) + ","
        sql += sqlStringConvert(request.context["txt_aline"]) + ","
        sql += 'CURRENT_TIMESTAMP' + ","
        sql += sqlStringConvert(request.cfs_ini["iniWsNo"]) + ')'
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC01_MODE0)
        request.context["gSetField"] = "txt_avesselcd"
    except Exception as e:
        __logger.error(e)
        request.context["cmd_entry_enable"] = False
        raise Exception(e)
        # TODO
        # OraError "TBVESSEL" & strProcTbl, sql


def cmd_change_Click(request):
    try:
        sql = "UPDATE TBVESSEL" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "SET VESSELNM = " + sqlStringConvert(request.context["txt_avesselnm"]) + ","
        sql += "CALLSIGN = " + sqlStringConvert(request.context["txt_acallsign"]) + ","
        sql += "OPECD = " + sqlStringConvert(request.context["txt_aopecd"]) + ","
        sql += "LPORTCD = " + sqlStringConvert(request.context["txt_alportcd"]) + ","
        sql += "BERTHNM = " + sqlStringConvert(request.context["txt_aberthnm"]) + ","
        sql += "LINE = " + sqlStringConvert(request.context["txt_aline"]) + ","
        sql += "UDATE = CURRENT_TIMESTAMP" + ","
        sql += "UWSID = " + sqlStringConvert(request.cfs_ini["iniWsNo"]) + " "
        sql += "WHERE VESSELCD = " + sqlStringConvert(request.context["txt_avesselcd"])
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC01_MODE0)
        request.context["gSetField"] = "txt_avesselcd"

    except Exception as e:
        __logger.error(e)
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise Exception(e)
        # TODO
        # OraError "TBVESSEL" & strProcTbl, sql


def cmd_delete_Click(request):
    sql = 'DELETE FROM TBVESSEL' + request.cfs_ini["iniUpdTbl"] + ' '
    sql += 'WHERE VESSELCD = ' + sqlStringConvert(request.context["txt_avesselcd"])
    try:
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC01_MODE0)
        request.context["gSetField"] = "txt_aopecd"
    except Exception as e:
        __logger.error(e)
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise Exception(e)
        # TODO
        # OraError "TBVESSEL" & strProcTbl, sql


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False

    init_form(request, CFSC01_MODE0)
    request.context["gSetField"] = "txt_avesselcd"


def init_form(request, intMode):
    if intMode == CFSC01_MODE0:
        request.context["txt_avesselcd"] = ""
    request.context["txt_avesselnm"] = ""
    request.context["txt_acallsign"] = ""
    request.context["txt_aopecd"] = ""
    request.context["lbl_aopenm"] = ""
    request.context["txt_alportcd"] = ""
    request.context["lbl_aportnm"] = ""
    request.context["txt_aberthnm"] = ""
    request.context["txt_aline"] = ""


def inpdatachk1(request):
    if not request.context["txt_avesselcd"]:
        # TODO
        # MsgDspWarning "必須入力エラー", "本船コードを入力して下さい。"
        request.context["gSetField"] = "txt_avesselcd"
        return FATAL_ERR
    return NOMAL_OK


def inpdatachk2(request):
    if request.context["txt_avesselnm"] == '':
        # TODO
        # MsgDspWarning "必須入力エラー", "本船名称を入力して下さい。"
        request.context["gSetField"] = "txt_avesselnm"
        return FATAL_ERR
    if len(request.context["txt_avesselnm"]) > 25:
        # TODO
        # MsgDspWarning "入力桁数エラー", "本船名称は" & txt_avesselnm.MaxLength & "桁以内で入力して下さい。"
        request.context["gSetField"] = "txt_avesselnm"
        return FATAL_ERR
    if request.context["txt_acallsign"] == "":
        # TODO
        # MsgDspWarning "必須入力エラー", "Callsignを入力して下さい。"
        request.context["gSetField"] = "txt_acallsign"
        return FATAL_ERR
    if request.context["txt_aopecd"] == "":
        # TODO
        # MsgDspWarning "必須入力エラー", "オペレータコードを入力して下さい。"
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR
    intRtn = TbOpe_TableCheck(request.context["txt_aopecd"], request.cfs_ini["iniUpdTbl"])
    if intRtn == DB_NOT_FIND:
        # TODO
        # MsgDspWarning "コード未登録エラー", "Operator Code Tableが登録されていません。"
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR
    elif intRtn == DB_FATAL_ERR:
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR

    if request.context["txt_alportcd"] == "":
        # TODO
        # MsgDspWarning "必須入力エラー", "着岸港コードを入力して下さい。"
        request.context["gSetField"] = "txt_alportcd"
        return FATAL_ERR
    intRtn = TbPort_TableCheck(request.context["txt_alportcd"], request.cfs_ini["iniUpdTbl"])
    if intRtn == DB_NOT_FIND:
        # TODO
        # MsgDspWarning "コード未登録エラー", "Port Code Tableが登録されていません。"
        request.context["gSetField"] = "txt_alportcd"
        return FATAL_ERR
    elif intRtn == DB_FATAL_ERR:
        request.context["gSetField"] = "txt_alportcd"
        return FATAL_ERR

    if request.context["txt_aberthnm"] == "":
        # TODO
        # MsgDspWarning "必須入力エラー", "着岸バース名称を入力して下さい。"
        request.context["gSetField"] = "txt_aberthnm"
        return FATAL_ERR

    if len(request.context["txt_aberthnm"]) > 25:
        # TODO
        # MsgDspWarning "入力桁数エラー", "着岸バース名称は" & txt_aberthnm.MaxLength & "桁以内で入力して下さい。"
        request.context["gSetField"] = "txt_aberthnm"
        return FATAL_ERR
    return NOMAL_OK


def Cm_TbOpeChk(request, strOpeCd):
    try:
        sql = "SELECT OPENM "
        sql += "FROM TBOPE" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "WHERE OPECD = " + sqlStringConvert(strOpeCd)
        return SqlExecute(sql).all()
    except Exception as e:
        __logger.error(e)
        raise Exception(e)
        # TODO
        # OraError "TBOPE" & strProcTbl, sql


def Cm_TbPortChk(request, strPortCd):
    try:
        sql = "SELECT PORTNM "
        sql += "FROM TBPORT" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "WHERE PORTCD = " + sqlStringConvert(strPortCd)
        return SqlExecute(sql).all()
    except Exception as e:
        __logger.error(e)
        raise Exception(e)
        # TODO
        # OraError "TBPORT" & strProcTbl, sql
