import logging

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute, Const
from main.common.function.Common import dbField, IsNumeric, DbDataChange
from main.common.function.Const import NOMAL_OK, FATAL_ERR
from main.common.function.DspMessage import MsgDspError
from main.common.utils import Response
from main.middleware.exception.exceptions import PostgresException

PROGID = "cfsm0300"
CFSC03_MODE0 = 0
CFSC03_MODE1 = 1
CFSC03_MINTON_MIN = 0
CFSC03_MINTON_MAX = 999

__logger = logging.getLogger(__name__)


@update_context()
@load_cfs_ini("menu4")
def f_cfsc0300(request):
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
        elif action == "txt_aopecd_Change":
            id_show_data = txt_aopecd_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        for index in range(3):
            if action == f"txt_adelchr{index}_LostFocus":
                id_show_data = txt_adelchr_LostFocus(request, index)
                return Response(request).json_response_event_js_html(id_show_data)
    else:
        Form_Load(request)
    return render(request, "menu/menu4/f_cfsc0300.html", request.context)


def Form_Load(request):
    init_form(request, CFSC03_MODE0)

    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False


def txt_adelchr_LostFocus(request, index):
    intLen = len(request.context[f"txt_adelchr{index}"])
    if intLen == 0:
        request.context[f"txt_adellen{index}"] = ""
    else:
        request.context[f"txt_adellen{index}"] = intLen
    return f"txt_adellen{index}"


def txt_aopecd_Change(request):
    request.context["txt_aopecd"] = request.context["txt_aopecd"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_aopecd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def cmd_search_Click(request):
    sql = ""
    try:
        init_form(request, CFSC03_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql += "SELECT * "
        sql += "FROM TBOPE" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "WHERE OPECD = " + dbField(request.context["txt_aopecd"])
        sql += " FOR UPDATE NOWAIT"

        RsTbOpe = SqlExecute(sql).all()
        if not RsTbOpe.Rows:
            request.context["cmd_entry_enable"] = True
        else:
            request.context["txt_aopenm"] = DbDataChange(RsTbOpe.Rows[0]["openm"])
            if DbDataChange(RsTbOpe.Rows[0]["nsendflg"]) == "Y":
                request.context["cmb_ansendflg"] = "0"
            elif DbDataChange(RsTbOpe.Rows[0]["nsendflg"]) == "N":
                request.context["cmb_ansendflg"] = "1"
            request.context["txt_ascaccd"] = DbDataChange(RsTbOpe.Rows[0]["scaccd"])
            if DbDataChange(RsTbOpe.Rows[0]["nscacflg"]) == "Y":
                request.context["cmb_anscacflg"] = "0"
            elif DbDataChange(RsTbOpe.Rows[0]["nsendflg"]) == "N":
                request.context["cmb_anscacflg"] = "1"

            request.context["txt_adelchr0"] = DbDataChange(RsTbOpe.Rows[0]["delchr1"])
            request.context["txt_adellen0"] = DbDataChange(RsTbOpe.Rows[0]["dellen1"])
            request.context["txt_adelchr1"] = DbDataChange(RsTbOpe.Rows[0]["delchr2"])
            request.context["txt_adellen1"] = DbDataChange(RsTbOpe.Rows[0]["dellen2"])
            request.context["txt_adelchr2"] = DbDataChange(RsTbOpe.Rows[0]["delchr3"])
            request.context["txt_adellen2"] = DbDataChange(RsTbOpe.Rows[0]["dellen3"])
            if DbDataChange(RsTbOpe.Rows[0]["opekbn"]) == "1":
                request.context["cmb_aopekbn"] = "0"
            elif DbDataChange(RsTbOpe.Rows[0]["opekbn"]) == "2":
                request.context["cmb_aopekbn"] = "1"
            request.context["txt_iminton"] = f'{DbDataChange(RsTbOpe.Rows[0]["minton"]):,}'
            if DbDataChange(RsTbOpe.Rows[0]["arearkbn"]) == "Y":
                request.context["cmb_aarearkbn"] = "0"
            elif DbDataChange(RsTbOpe.Rows[0]["arearkbn"]) == "N":
                request.context["cmb_aarearkbn"] = "1"

            request.context["cmd_change_enable"] = True
            request.context["cmd_delete_enable"] = True
        request.context["gSetField"] = "txt_aopenm"
    except Exception as e:
        raise PostgresException(Error=e, DbTbl="TBOPE" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_entry_Click(request):
    sql = ""
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return

        sql += "INSERT INTO TBOPE" + request.cfs_ini["iniUpdTbl"] + ' '
        sql += "(OPECD,OPENM,NSENDFLG,NSCACFLG,SCACCD,MINTON,OPEKBN,"
        sql += "DELCHR1,DELCHR2,DELCHR3,DELLEN1,DELLEN2,DELLEN3,AREARKBN,UDATE,UWSID) "
        sql += 'VALUES('
        sql += dbField(request.context["txt_aopecd"]) + ","
        sql += dbField(request.context["txt_aopenm"]) + ","
        if request.context["cmb_ansendflg"] == "0":
            sql += dbField("Y") + ","
        elif request.context["cmb_ansendflg"] == "1":
            sql += dbField("N") + ","
        if request.context["cmb_anscacflg"] == "0":
            sql += dbField("Y") + ","
        elif request.context["cmb_ansendflg"] == "1":
            sql += dbField("N") + ","
        sql += dbField(request.context["txt_ascaccd"]) + ","
        sql += request.context["txt_iminton"] + ","
        if request.context["cmb_aopekbn"] == "0":
            sql += dbField("1") + ","
        elif request.context["cmb_aopekbn"] == "1":
            sql += dbField("2") + ","
        sql += dbField(request.context["txt_adelchr0"]) + ","
        sql += dbField(request.context["txt_adelchr1"]) + ","
        sql += dbField(request.context["txt_adelchr2"]) + ","
        sql += dbField(request.context["txt_adellen0"]) + ","
        sql += dbField(request.context["txt_adellen1"]) + ","
        sql += dbField(request.context["txt_adellen2"]) + ","
        if request.context["cmb_aarearkbn"] == "0":
            sql += dbField("Y") + ","
        elif request.context["cmb_aarearkbn"] == "1":
            sql += dbField("N") + ","
        sql += 'CURRENT_TIMESTAMP' + ","
        sql += dbField(request.cfs_ini["iniWsNo"]) + ')'
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC03_MODE0)
        request.context["gSetField"] = "txt_aopecd"
    except Exception as e:
        request.context["cmd_entry_enable"] = False
        raise PostgresException(Error=e, DbTbl="TBOPE" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_change_Click(request):
    sql = ""
    try:
        sql += "UPDATE TBOPE" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "SET OPENM = " + dbField(request.context["txt_aopenm"]) + ","
        if request.context["cmb_ansendflg"] == "0":
            sql += "NSENDFLG =" + dbField("Y") + ","
        elif request.context["cmb_ansendflg"] == "1":
            sql += "NSENDFLG =" + dbField("N") + ","
        if request.context["cmb_anscacflg"] == "0":
            sql += "NSCACFLG =" + dbField("Y") + ","
        elif request.context["cmb_ansendflg"] == "1":
            sql += "NSCACFLG =" + dbField("N") + ","
        sql += "SCACCD =" + dbField(request.context["txt_ascaccd"]) + ","
        sql += "MINTON =" + request.context["txt_iminton"] + ","
        if request.context["cmb_aopekbn"] == "0":
            sql += "OPEKBN =" + dbField("1") + ","
        elif request.context["cmb_aopekbn"] == "1":
            sql += "OPEKBN =" + dbField("2") + ","
        sql += "DELCHR1 =" + dbField(request.context["txt_adelchr0"]) + ","
        sql += "DELCHR2 =" + dbField(request.context["txt_adelchr1"]) + ","
        sql += "DELCHR3 =" + dbField(request.context["txt_adelchr2"]) + ","
        sql += "DELLEN1 =" + dbField(request.context["txt_adellen0"]) + ","
        sql += "DELLEN2 =" + dbField(request.context["txt_adellen1"]) + ","
        sql += "DELLEN3 =" + dbField(request.context["txt_adellen2"]) + ","
        if request.context["cmb_aarearkbn"] == "0":
            sql += "AREARKBN =" + dbField("Y") + ","
        elif request.context["cmb_aarearkbn"] == "1":
            sql += "AREARKBN =" + dbField("N") + ","
        sql += "UDATE = CURRENT_TIMESTAMP" + ","
        sql += "UWSID = " + dbField(request.cfs_ini["iniWsNo"]) + " "
        sql += "WHERE OPECD = " + dbField(request.context["txt_aopecd"])
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC03_MODE0)
        request.context["gSetField"] = "txt_aopecd"

    except Exception as e:
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise PostgresException(Error=e, DbTbl="TBOPE" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_delete_Click(request):
    sql = "SELECT COUNT(OPECD) AS DCNT "
    sql += "FROM TBFREETM" + request.cfs_ini["iniUpdTbl"] + " "
    sql += "WHERE OPECD = " + dbField(request.context["txt_aopecd"])
    RsTbFreeTm = SqlExecute(sql).all()
    if RsTbFreeTm.Rows[0]["dcnt"] == 0:
        MsgDspError(request, Const.MSG_DSP_WARN, "削除エラー", "フリータイムコードテーブルが存在する為、削除できません。")

    sql = "SELECT COUNT(OPECD) AS DCNT "
    sql += "FROM TBDEMURG" + request.cfs_ini["iniUpdTbl"] + " "
    sql += "WHERE OPECD = " + dbField(request.context["txt_aopecd"])
    RsTbDemurg = SqlExecute(sql).all()
    if RsTbDemurg.Rows[0]["dcnt"] == 0:
        MsgDspError(request, Const.MSG_DSP_WARN, "削除エラー", "デマレージテーブルが存在する為、削除できません。")
    sql = 'DELETE FROM TBOPE' + request.cfs_ini["iniUpdTbl"] + " "
    sql += 'WHERE OPECD = ' + dbField(request.context["txt_aopecd"])
    try:
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC03_MODE0)
        request.context["gSetField"] = "txt_aopecd"
    except Exception as e:
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise PostgresException(Error=e, DbTbl="TBOPE" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False

    init_form(request, CFSC03_MODE0)
    request.context["gSetField"] = "txt_aopecd"


def init_form(request, intMode):
    if intMode == CFSC03_MODE0:
        request.context["txt_aopecd"] = ""
    request.context["txt_aopenm"] = ""
    request.context["cmb_ansendflg"] = "0"
    request.context["txt_ascaccd"] = ""
    request.context["cmb_anscacflg"] = "0"
    for i in range(3):
        request.context[f"txt_adelchr{i}"] = ""
        request.context[f"txt_adellen{i}"] = ""
    request.context["cmb_aopekbn"] = "0"
    request.context["txt_iminton"] = ""
    request.context["cmb_aarearkbn"] = "1"
    request.context["txt_iminton"] = "1"


def inpdatachk1(request):
    if not request.context["txt_aopecd"]:
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "オペレータコードを入力して下さい。")
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR
    return NOMAL_OK


def inpdatachk2(request):
    if request.context["txt_aopenm"] == '':
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "オペレータ名称を入力して下さい。")
        request.context["gSetField"] = "txt_aopenm"
        return FATAL_ERR
    if len(request.context["txt_aopenm"]) > 25:
        MsgDspError(request, Const.MSG_DSP_WARN, "入力桁数エラー",
                    "オペレータ名称は" + str(request.context["txt_aopenm"]) + "桁以内で入力して下さい。")
        request.context["gSetField"] = "txt_aopenm"
        return FATAL_ERR
    if request.context["cmb_anscacflg"] == "0":
        if request.context["txt_ascaccd"] == "":
            MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー",
                        "貨物管理番号編集識別が、" + "編集時にＳＣＡＣコード付加する" + "の場合、" + "ＳＣＡＣコードを入力して下さい。")
            request.context["gSetField"] = "txt_ascaccd"
            return FATAL_ERR
    if request.context["txt_iminton"] == "":
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "ミニマム屯数を入力して下さい。")
        request.context["gSetField"] = "txt_iminton"
        return FATAL_ERR
    if not IsNumeric(request.context["txt_iminton"]):
        MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー", "ミニマム屯数は整数(ZZ9形式)で入力して下さい。")
        request.context["gSetField"] = "txt_iminton"
        return FATAL_ERR
    if CFSC03_MINTON_MIN > float(request.context["txt_iminton"]) or CFSC03_MINTON_MAX < float(
            request.context["txt_iminton"]):
        MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー",
                    "ミニマム屯数は" + str(CFSC03_MINTON_MIN) + "から" + str(CFSC03_MINTON_MAX) + "以内で入力して下さい。")
        request.context["gSetField"] = "txt_iminton"
        return FATAL_ERR
    return NOMAL_OK
