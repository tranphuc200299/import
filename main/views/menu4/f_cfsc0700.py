import logging
from django.db import IntegrityError, transaction
from django.shortcuts import render
from main.common.decorators import update_context, load_cfs_ini
from main.common.function import SqlExecute
from main.common.function.Common import DbDataChange, sqlStringConvert, dbField, IsNumeric, dbsingle
from main.common.function.DspMessage import MsgDspError
from main.common.function.Const import NOMAL_OK, FATAL_ERR, DB_NOT_FIND, DB_FATAL_ERR, MSG_DSP_WARN, \
    csSTANKAKBN_1, csSTANKAKBN_2, csSTANKAKBN_3, csSTANKAKBN_4, csSTANKAKBN_5, csDCALC_1, csDCALC_2, csDCALC_3
from main.common.function.TableCheck import TbOpe_TableCheck, TbPort_TableCheck
from main.common.utils import Response
from main.middleware.exception.exceptions import (
    PostgresException
)

__logger = logging.getLogger(__name__)

PROGID = "cfsm0700"
CFSC07_MODE0 = 0
CFSC07_MODE1 = 1
CFSC07_RANK_MIN = 1  # 超過日数Min値
CFSC07_RANK_MAX = 999  # 超過日数Max値
CFSC07_TANKA_MIN = 0  # 単価Min値
CFSC07_TANKA_MAX = 99999999  # 単価Max値


@update_context()
@load_cfs_ini("menu4")
def f_cfsc0700(request):
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
        elif action == "txt_itanka_LostFocus":
            id_show_data = txt_itanka_LostFocus(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_itankac_LostFocus":
            id_show_data = txt_itankac_LostFocus(request)
            return Response(request).json_response_event_js_html(id_show_data)
    else:
        Form_Load(request)
    return render(request, "menu/menu4/f_cfsc0700.html", request.context)


def Form_Load(request):
    init_form(request, CFSC07_MODE0)
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False


def init_form(request, intMode):
    if intMode == CFSC07_MODE0:
        request.context["txt_aopecd"] = ""

    for i in range(1, 6):
        request.context["txt_irank" + str(i)] = ""
        request.context["txt_itanka" + str(i)] = ""
    request.context["cmb_astankakbn"] = "0"
    request.context["txt_itankac"] = ""
    request.context["cmb_afcalc"] = "0"


def txt_itanka_LostFocus(request):
    if not request.context["txt_itanka"] != "":
        if not IsNumeric(request.context["txt_itanka"]):
            request.context["gSetField"] = "txt_itanka"
            MsgDspError(request, MSG_DSP_WARN, "入力整合性エラー", "単価は整数(\ZZ,ZZZ,ZZ9形式)で入力して下さい。")
            return "txt_itanka"

        if CFSC07_TANKA_MIN > int(request.context["txt_itanka"]) or CFSC07_TANKA_MAX < int(
                request.context["txt_itanka"]):
            request.context["gSetField"] = "txt_itanka"
            MsgDspError(request, MSG_DSP_WARN, "入力整合性エラー",
                        "単価は" + f"{CFSC07_TANKA_MIN :,.1f}" + "から" + f"{CFSC07_TANKA_MAX :,.1f}" + "以内で入力して下さい。")
            return "txt_itanka"
        request.context["txt_itanka"] = f"{float(request.context['txt_itanka']) :,.1f}"
        return "txt_itanka"


def txt_itankac_LostFocus(request):
    if request.context["txt_itankac"] != "":
        if not IsNumeric(request.context["txt_itankac"]):
            request.context["gSetField"] = "txt_itankac"
            MsgDspError(request, MSG_DSP_WARN, "入力整合性エラー", "名古屋用加算単価は整数(\ZZ,ZZZ,ZZ9形式)で入力して下さい。")
            return "txt_itankac"
        if CFSC07_TANKA_MIN > int(request.context["txt_itankac"]) or CFSC07_TANKA_MAX < int(
                request.context["txt_itankac"]):
            request.context["gSetField"] = "txt_itankac"
            MsgDspError(request, MSG_DSP_WARN, "入力整合性エラー",
                        "名古屋用加算単価は" + f"{CFSC07_TANKA_MIN :,.1f}" + "から" + f"{CFSC07_TANKA_MAX :,.1f}" + "以内で入力して下さい。")
            return "txt_itankac"

        request.context["txt_itankac"] = f"{float(request.context['txt_itankac']) :,.1f}"
        return "txt_itankac"


def txt_aopecd_Change(request):
    request.context["txt_aopecd"] = request.context["txt_aopecd"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_aopecd", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def inpdatachk1(request):
    if not request.context["txt_aopecd"]:

        MsgDspError(request, MSG_DSP_WARN, "必須入力エラー", "オペレータコードを入力して下さい。")
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR
    intRtn = TbOpe_TableCheck(request.context["txt_aopecd"], request.cfs_ini["iniUpdTbl"])
    if intRtn == DB_NOT_FIND:
        MsgDspError(request, MSG_DSP_WARN, "コード未登録エラー", "Operator Code Tableが登録されていません。")
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR
    elif intRtn == DB_FATAL_ERR:
        request.context["gSetField"] = "txt_aopecd"
        return FATAL_ERR
    return NOMAL_OK


def cmd_search_Click(request):
    sql = ""
    try:
        init_form(request, CFSC07_MODE1)
        if inpdatachk1(request) != NOMAL_OK:
            return
        sql = "SELECT * "
        sql += "FROM TBDEMURG" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "WHERE OPECD = " + dbField(request.context["txt_aopecd"])
        sql += " FOR UPDATE NOWAIT"
        RsTbDemurg = SqlExecute(sql).all()
        if not RsTbDemurg.Rows:
            request.context["cmd_entry_enable"] = True
        else:
            for i in range(1, 6):
                if DbDataChange(RsTbDemurg.Rows[0]["rank" + str(i)]) != 0:
                    request.context["txt_irank" + str(i)] = DbDataChange(RsTbDemurg.Rows[0]["rank" + str(i)])
                if DbDataChange(RsTbDemurg.Rows[0]["tanka" + str(i)]) != 0:
                    request.context[
                        "txt_itanka" + str(i)] = f"{float(DbDataChange(RsTbDemurg.Rows[0]['tanka' + str(i)])):,.1f}"
            if DbDataChange(RsTbDemurg.Rows[0]["stankakbn"]) == csSTANKAKBN_1:
                request.context["cmb_astankakbn"] = "0"
            elif DbDataChange(RsTbDemurg.Rows[0]["stankakbn"]) == csSTANKAKBN_2:
                request.context["cmb_astankakbn"] = "2"
            elif DbDataChange(RsTbDemurg.Rows[0]["stankakbn"]) == csSTANKAKBN_3:
                request.context["cmb_astankakbn"] = "4"
            elif DbDataChange(RsTbDemurg.Rows[0]["stankakbn"]) == csSTANKAKBN_4:
                request.context["cmb_astankakbn"] = "1"
            elif DbDataChange(RsTbDemurg.Rows[0]["stankakbn"]) == csSTANKAKBN_5:
                request.context["cmb_astankakbn"] = "3"
            if DbDataChange(RsTbDemurg.Rows[0]["tankac"]) != 0:
                request.context["txt_itankac"] = DbDataChange(RsTbDemurg.Rows[0]["tankac"])
            if DbDataChange(RsTbDemurg.Rows[0]["dcalc"]) == csDCALC_1:
                request.context["cmb_afcalc"] = "0"
            elif DbDataChange(RsTbDemurg.Rows[0]["dcalc"]) == csDCALC_2:
                request.context["cmb_afcalc"] = "1"
            elif DbDataChange(RsTbDemurg.Rows[0]["dcalc"]) == csDCALC_3:
                request.context["cmb_afcalc"] = "2"
        request.context["cmd_change_enable"] = True
        request.context["cmd_delete_enable"] = True
        request.context["gSetField"] = "txt_irank1"
    except IntegrityError as e:
        __logger.error(e)
        raise PostgresException(Error=e, DbTbl="TBDEMURG" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def inpdatachk2(request):
    try:
        for i in range(1, 6):
            if request.context["txt_irank" + str(i)] != '':
                if not IsNumeric(request.context["txt_irank" + str(i)]):
                    MsgDspError(request, MSG_DSP_WARN, "入力整合性エラー", "超過日数は整数(ZZ9形式)で入力して下さい。")
                    request.context["gSetField"] = "txt_irank" + str(i)
                    return FATAL_ERR
                if CFSC07_RANK_MIN > float(request.context["txt_irank" + str(i)]) or CFSC07_RANK_MAX < float(
                        request.context["txt_irank" + str(i)]):
                    MsgDspError(request, MSG_DSP_WARN, "入力整合性エラー",
                                "超過日数は{}から{}以内で入力して下さい。".format(CFSC07_RANK_MIN, CFSC07_RANK_MAX))
                    request.context["gSetField"] = "txt_irank" + str(i)
                    return FATAL_ERR
            if request.context["txt_itanka" + str(i)] != '':
                if not IsNumeric(request.context["txt_itanka" + str(i)]):
                    MsgDspError(request, MSG_DSP_WARN, "入力整合性エラー", "単価は整数(\ZZ,ZZZ,ZZ9形式)で入力して下さい。")
                    request.context["gSetField"] = "txt_itanka" + str(i)
                    return FATAL_ERR
                if CFSC07_RANK_MIN > float(request.context["txt_itanka" + str(i)]) or CFSC07_RANK_MAX < float(
                        request.context["txt_itanka" + str(i)]):
                    MsgDspError(request, MSG_DSP_WARN, "入力整合性エラー",
                                "単価は" + f"{CFSC07_TANKA_MIN :,.1f}" + "から" + f"{CFSC07_TANKA_MAX :,.1f}" + "以内で入力して下さい。")
                    request.context["gSetField"] = "txt_itanka" + str(i)
                    return FATAL_ERR
            if request.context["txt_irank" + str(i)] != '' and request.context["txt_itanka" + str(i)] == '':
                MsgDspError(request, MSG_DSP_WARN, "整合性エラー", "超過日数と単価はセットで入力して下さい。")
                request.context["gSetField"] = "txt_itanka" + str(i)
                return FATAL_ERR
            if i == 1:
                if request.context["txt_irank" + str(i)] == "":
                    MsgDspError(request, MSG_DSP_WARN, "必須入力エラー", "超過日数(1)を入力して下さい。")
                    request.context["gSetField"] = "txt_irank1"
                    return FATAL_ERR
            else:
                if request.context["txt_irank" + str(i)] != "":
                    if request.context["txt_irank" + str(i - 1)] >= request.context["txt_irank" + str(i)]:
                        MsgDspError(request, MSG_DSP_WARN, "整合性エラー",
                                    "超過日数({}) < 超過日数({})の関係で入力して下さい。".format(i, i + 1))
                        request.context["gSetField"] = "txt_irank" + str(i)
                        return FATAL_ERR
        if request.context["txt_itankac"] != "":
            if not IsNumeric(request.context["txt_itankac"]):
                MsgDspError(request, MSG_DSP_WARN, "入力整合性エラー", "名古屋用加算単価は整数(\ZZ,ZZZ,ZZ9形式)で入力して下さい。")
                request.context["gSetField"] = "txt_itankac"
                return FATAL_ERR
            if CFSC07_TANKA_MIN > float(request.context["txt_itankac"]) or CFSC07_TANKA_MAX < float(
                    request.context["txt_itankac"]):
                MsgDspError(request, MSG_DSP_WARN, "入力整合性エラー",
                            "名古屋用加算単価は" + f"{CFSC07_TANKA_MIN :,.1f}" + "から" + f"{CFSC07_TANKA_MAX :,.1f}" + "以内で入力して下さい。")
                request.context["gSetField"] = "txt_itankac"
                return FATAL_ERR
            request.context["txt_itankac"] = f"{float(request.context['txt_itankac']) :,.1f}"
        return NOMAL_OK
    except Exception as e:
        import os, sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


def cmd_entry_Click(request):
    sql = ""
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        sql = "INSERT INTO TBDEMURG" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "(OPECD,RANK1,RANK2,RANK3,RANK4,RANK5,"
        sql += "TANKA1,TANKA2,TANKA3,TANKA4,TANKA5,STANKAKBN,TANKAC,DCALC,UDATE,UWSID) "
        sql += "VALUES("
        sql += dbField(request.context["txt_aopecd"]) + ","
        for intCnt in range(1, 6):
            sql += f"{dbsingle(request.context['txt_irank' + str(intCnt)])},"
        for intCnt in range(1, 6):
            sql += f"{dbsingle(request.context['txt_itanka' + str(intCnt)])},"
        if request.context["cmb_astankakbn"] == "0":
            sql += dbField(csSTANKAKBN_1) + ","
        elif request.context["cmb_astankakbn"] == "1":
            sql += dbField(csSTANKAKBN_4) + ","
        elif request.context["cmb_astankakbn"] == "2":
            sql += dbField(csSTANKAKBN_2) + ","
        elif request.context["cmb_astankakbn"] == "3":
            sql += dbField(csSTANKAKBN_5) + ","
        elif request.context["cmb_astankakbn"] == "4":
            sql += dbField(csSTANKAKBN_3) + ","
        sql += f"{dbsingle(request.context['txt_itankac'])},"
        if request.context["cmb_afcalc"] == "0":
            sql += dbField(csDCALC_1) + ","
        elif request.context["cmb_afcalc"] == "1":
            sql += dbField(csDCALC_2) + ","
        elif request.context["cmb_afcalc"] == "2":
            sql += dbField(csDCALC_3) + ","
        sql += "CURRENT_TIMESTAMP" + ","
        sql += dbField(request.cfs_ini["iniWsNo"]) + ")"
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC07_MODE0)
        request.context["gSetField"] = "txt_aopecd"
    except IntegrityError as e:
        request.context["cmd_entry_enable"] = False
        __logger.error(e)
        raise PostgresException(Error=e, DbTbl="TBDEMURG" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_change_Click(request):
    sql = ""
    try:
        if inpdatachk2(request) != NOMAL_OK:
            return
        sql = "UPDATE TBDEMURG" + request.cfs_ini["iniUpdTbl"] + " "
        sql += f"SET RANK1 = {dbsingle(request.context['txt_irank1'])},"
        sql += f"RANK2 = {dbsingle(request.context['txt_irank2'])},"
        sql += f"RANK3 = {dbsingle(request.context['txt_irank3'])},"
        sql += f"RANK4 = {dbsingle(request.context['txt_irank4'])},"
        sql += f"RANK5 = {dbsingle(request.context['txt_irank5'])},"
        sql += f"TANKA1 = {dbsingle(request.context['txt_itanka1'])},"
        sql += f"TANKA2 = {dbsingle(request.context['txt_itanka2'])},"
        sql += f"TANKA3 = {dbsingle(request.context['txt_itanka3'])},"
        sql += f"TANKA4 = {dbsingle(request.context['txt_itanka4'])},"
        sql += f"TANKA5 = {dbsingle(request.context['txt_itanka5'])},"
        if request.context["cmb_astankakbn"] == "0":
            sql += "STANKAKBN = " + dbField(csSTANKAKBN_1) + ","
        elif request.context["cmb_astankakbn"] == "1":
            sql += "STANKAKBN = " + dbField(csSTANKAKBN_4) + ","
        elif request.context["cmb_astankakbn"] == "2":
            sql += "STANKAKBN = " + dbField(csSTANKAKBN_2) + ","
        elif request.context["cmb_astankakbn"] == "3":
            sql += "STANKAKBN = " + dbField(csSTANKAKBN_5) + ","
        elif request.context["cmb_astankakbn"] == "4":
            sql += "STANKAKBN = " + dbField(csSTANKAKBN_3) + ","
        sql += f"TANKAC = {dbsingle(request.context['txt_itankac'])},"
        if request.context["cmb_afcalc"] == "0":
            sql += "DCALC = " + dbField(csDCALC_1) + ","
        elif request.context["cmb_afcalc"] == "1":
            sql += "DCALC = " + dbField(csDCALC_2) + ","
        elif request.context["cmb_afcalc"] == "2":
            sql += "DCALC = " + dbField(csDCALC_3) + ","
        sql += "UDATE = CURRENT_TIMESTAMP" + ","
        sql += "UWSID = " + dbField(request.cfs_ini["iniWsNo"]) + " "
        sql += "WHERE OPECD = " + dbField(request.context["txt_aopecd"])
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC07_MODE0)
        request.context["gSetField"] = "txt_aopecd"
    except IntegrityError as e:
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        __logger.error(e)
        raise PostgresException(Error=e, DbTbl="TBDEMURG" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)

    except Exception as e:
        __logger.error(e)
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise Exception(e)


def cmd_delete_Click(request):
    sql = "DELETE FROM TBDEMURG" + request.cfs_ini["iniUpdTbl"] + " "
    sql += "WHERE OPECD = " + dbField(request.context["txt_aopecd"])
    try:
        with transaction.atomic():
            SqlExecute(sql).execute()
        init_form(request, CFSC07_MODE0)
        request.context["gSetField"] = "txt_aopecd"
    except IntegrityError as e:
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        __logger.error(e)
        raise PostgresException(Error=e, DbTbl="TBDEMURG" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)
    except Exception as e:
        __logger.error(e)
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise Exception(e)


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False

    init_form(request, CFSC07_MODE0)
    request.context["gSetField"] = "txt_aopecd"
