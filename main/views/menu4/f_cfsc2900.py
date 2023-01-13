import logging
from datetime import datetime

from django.db import transaction
from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini
from main.common.function import Common, Const
from main.common.function.DspMessage import MsgDspError
from main.common.utils import Response
from main.middleware.exception.exceptions import PostgresException

__logger = logging.getLogger(__name__)

PROGID = "cfsm2900"
CFSC29_MODE0 = 0
CFSC29_MODE1 = 1
CFSC29_LBL_MAX = 41
CFSC29_DAYKBN_WEK = ""
CFSC29_DAYKBN_SAT = "土曜"
CFSC29_DAYKBN_SUN = "日曜"
CFSC29_DAYKBN_HOL = "祝日"
CFSC29_DAYKBN_COL_WEK = "&HFFC0C0"
CFSC29_DAYKBN_COL_SAT = "&HFF8080"
CFSC29_DAYKBN_COL_SUN = "&H8080FF"
CFSC29_DAYKBN_COL_HOL = "&H8080FF"
CFSC29_YEAR_MIN = 1
CFSC29_YEAR_MAX = 12


@update_context()
@load_cfs_ini("menu4")
def f_cfsc2900(request):
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "cmd_search":
            cmd_search_Click(request)
        elif action == "txt_ayear_Change":
            id_show_data = txt_ayear_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_amonth_Change":
            id_show_data = txt_amonth_Change(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_ayear_LostFocus":
            id_show_data = txt_ayear_LostFocus(request)
            return Response(request).json_response_event_js_html(id_show_data)
        elif action == "txt_amonth_LostFocus":
            id_show_data = txt_amonth_LostFocus(request)
            return Response(request).json_response_event_js_html(id_show_data)
        if action.startswith("txt_adaytp"):
            for i in range(31):
                if action == f"txt_adaytp{i}_Click":
                    id_show_data = txt_adaytp_Click(request, i)
                    return Response(request).json_response_event_js_html(id_show_data)
    else:
        Form_Load(request)
    return render(request, "menu/menu4/f_cfsc2900.html", request.context)


def Form_Load(request):
    init_form(request, CFSC29_MODE0)

    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False


def txt_ayear_LostFocus(request):
    if not request.context["txt_ayear"]:
        if not Common.IsNumeric(request.context["txt_ayear"]):
            MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー", "年は整数(9999形式)で入力して下さい。")
            request.context["gSetField"] = "txt_ayear"
            return Const.FATAL_ERR
        request.context["txt_ayear"] = f"{request.context['txt_ayear']:04}"
    return Const.NOMAL_OK


def txt_amonth_LostFocus(request):
    if not request.context["txt_amonth"]:
        if not Common.IsNumeric(request.context["txt_amonth"]):
            MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー", "月は整数(99形式)で入力して下さい。")
            request.context["gSetField"] = "txt_amonth"
            return Const.FATAL_ERR
        if CFSC29_YEAR_MIN > int(request.context["txt_amonth"]) or CFSC29_YEAR_MAX < int(request.context["txt_amonth"]):
            MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー",
                        "年は" + CFSC29_YEAR_MIN + "から" & CFSC29_YEAR_MAX & "以内で入力して下さい。")
            request.context["gSetField"] = "txt_amonth"
            return Const.FATAL_ERR
        request.context["txt_amonth"] = f"{request.context['txt_amonth']:02}"
    return Const.NOMAL_OK


def txt_adaytp_Click(request, index):
    txt_adaytp = request.context[f"txt_adaytp{index}"]
    if txt_adaytp == CFSC29_DAYKBN_WEK:
        request.context[f"txt_adaytp{index}_Caption"] = CFSC29_DAYKBN_SAT
        request.context[f"txt_adaytp{index}_BackColor"] = CFSC29_DAYKBN_COL_SAT
        request.context[f"txt_aday{index}_BackColor"] = CFSC29_DAYKBN_COL_SAT
    elif txt_adaytp == CFSC29_DAYKBN_SAT:
        request.context[f"txt_adaytp{index}_Caption"] = CFSC29_DAYKBN_SUN
        request.context[f"txt_adaytp{index}_BackColor"] = CFSC29_DAYKBN_COL_SUN
        request.context[f"txt_aday{index}_BackColor"] = CFSC29_DAYKBN_COL_SUN
    elif txt_adaytp == CFSC29_DAYKBN_SUN:
        request.context[f"txt_adaytp{index}_Caption"] = CFSC29_DAYKBN_HOL
        request.context[f"txt_adaytp{index}_BackColor"] = CFSC29_DAYKBN_COL_HOL
        request.context[f"txt_aday{index}_BackColor"] = CFSC29_DAYKBN_COL_HOL
    elif txt_adaytp == CFSC29_DAYKBN_HOL:
        request.context[f"txt_adaytp{index}_Caption"] = CFSC29_DAYKBN_WEK
        request.context[f"txt_adaytp{index}_BackColor"] = CFSC29_DAYKBN_COL_WEK
        request.context[f"txt_aday{index}_BackColor"] = CFSC29_DAYKBN_COL_WEK


def txt_ayear_Change(request):
    request.context["txt_ayear"] = request.context["txt_ayear"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_ayear", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def txt_amonth_Change(request):
    request.context["txt_amonth"] = request.context["txt_amonth"].upper()
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False
    return ["txt_amonth", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def cmd_search_Click(request):
    sql = ""
    try:
        init_form(request, CFSC29_MODE1)
        if inpdatachk1(request) != Const.NOMAL_OK:
            return
        first_day_month = datetime.strptime(f"{request.context['txt_ayear']}/{request.context['txt_amonth']}/01",
                                            "%Y/%m/%d")
        day_name = first_day_month.strftime('%A')
        if day_name == "Sunday":
            intStrLbl = 0
        elif day_name == "Monday":
            intStrLbl = 1
        elif day_name == "Tuesday":
            intStrLbl = 2
        elif day_name == "Wednesday":
            intStrLbl = 3
        elif day_name == "Thursday":
            intStrLbl = 4
        elif day_name == "Friday":
            intStrLbl = 5
        elif day_name == "Saturday":
            intStrLbl = 6
        strEndDt = datetime.date(int(request.context["txt_ayear"]), int(request.context["txt_amonth"]) + 1,
                                 1) - datetime.timedelta(days=1)
        intLoopCnt = Common.CmfDateFmt(strEndDt, "%d")

        for intCnt in range(1, intLoopCnt + 1):
            request.context[f"txt_aday{intStrLbl - 1 + intCnt}"] = intCnt

        for intCnt in range(CFSC29_LBL_MAX + 1):
            if request.context[f"txt_aday{intCnt}"] == "":
                request.context[f"txt_aday{intCnt}_Enabled"] = False
                request.context[f"txt_adaytp{intCnt}_Enabled"] = False

        sql += "SELECT * "
        sql += "FROM TBCALENDER" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "WHERE YMDATE = " + Common.dbField(request.context["txt_ayear"] + "/" + request.context["txt_amonth"])
        sql += " FOR UPDATE NOWAIT"
        RsTbCalender = Common.SqlExecute(sql).all()
        if not RsTbCalender.Rows:
            for intCnt in range(CFSC29_LBL_MAX + 1):
                if request.context[f"txt_aday{intCnt}"] != "":
                    if intCnt == 0 or intCnt % 7 == 0:
                        request.context[f"txt_adaytp{intCnt}_Caption"] = CFSC29_DAYKBN_SUN
                        request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_SUN
                        request.context[f"txt_aday{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_SUN
                    if intCnt % 7 == 6:
                        request.context[f"txt_adaytp{intCnt}_Caption"] = CFSC29_DAYKBN_SAT
                        request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_SAT
                        request.context[f"txt_aday{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_SAT
            HolidaySet_proc(request)
            request.context["cmd_entry_Enabled"] = True
        else:
            strDayKbn = Common.DbDataChange(RsTbCalender.Rows[0]["daykbn"])

            for intCnt in (len(strDayKbn)):
                if strDayKbn[intCnt] == Const.csDAYKBN_1:
                    pass
                elif strDayKbn[intCnt] == Const.csDAYKBN_2:
                    request.context[f"txt_adaytp{((intStrLbl - 1) + intCnt)}_Caption"] = CFSC29_DAYKBN_SAT
                    request.context[f"txt_adaytp{((intStrLbl - 1) + intCnt)}_BackColor"] = CFSC29_DAYKBN_COL_SAT
                    request.context[f"txt_aday{((intStrLbl - 1) + intCnt)}_BackColor"] = CFSC29_DAYKBN_COL_SAT
                elif strDayKbn[intCnt] == Const.csDAYKBN_3:
                    request[f"txt_adaytp{((intStrLbl - 1) + intCnt)}_Caption"] = CFSC29_DAYKBN_SUN
                    request[f"txt_adaytp{((intStrLbl - 1) + intCnt)}_BackColor"] = CFSC29_DAYKBN_COL_SUN
                    request[f"txt_aday{((intStrLbl - 1) + intCnt)}_BackColor"] = CFSC29_DAYKBN_COL_SUN
                elif strDayKbn[intCnt] == Const.csDAYKBN_4:
                    request.context[f"txt_adaytp{((intStrLbl - 1) + intCnt)}_Caption"] = CFSC29_DAYKBN_HOL
                    request.context[f"txt_adaytp{((intStrLbl - 1) + intCnt)}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                    request.context[f"txt_aday{((intStrLbl - 1) + intCnt)}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                if strDayKbn[intCnt] == Const.csDAYKBN_9:
                    break
            request.context["cmd_change_enable"] = True
            request.context["cmd_delete_enable"] = True
    except Exception as e:
        raise PostgresException(Error=str(e), DbTbl="TBCALENDER" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_entry_Click(request):
    sql = ""
    try:
        strDayKbn = ""
        if inpdatachk2(request) != Common.NOMAL_OK:
            return
        for intCnt1 in range(CFSC29_LBL_MAX + 1):
            if request.context[f"txt_aday{intCnt1}"] == "":
                continue
            for intCnt2 in range(31 - 1 + 1):
                if request.context[f"txt_aday{intCnt1 + intCnt2}"] != "":
                    txt_adaytp = request.context[f"txt_adaytp{intCnt1 + intCnt2}"]
                    if txt_adaytp == CFSC29_DAYKBN_WEK:
                        strDayKbn += Const.csDAYKBN_1
                    if txt_adaytp == CFSC29_DAYKBN_SAT:
                        strDayKbn += Const.csDAYKBN_2
                    if txt_adaytp == CFSC29_DAYKBN_SUN:
                        strDayKbn += Const.csDAYKBN_3
                    if txt_adaytp == CFSC29_DAYKBN_HOL:
                        strDayKbn += Const.csDAYKBN_4
                else:
                    strDayKbn += Const.csDAYKBN_9
            break
        sql += "INSERT INTO TBCALENDER" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "(YMDATE,DAYKBN,UDATE,UWSID) "
        sql += "VALUES("
        sql += Common.dbField(request.context["txt_ayear"] + "/" + request.context["txt_amonth"]) + ","
        sql += Common.dbField(strDayKbn) + ","
        sql += "CURRENT_TIMESTAMP" + ","
        sql += Common.dbField(request.cfs_ini["iniWsNo"]) + ")"
        with transaction.atomic():
            Common.SqlExecute(sql).execute()
        init_form(request, CFSC29_MODE0)
        request.context["gSetField"] = "txt_ayear"
    except Exception as e:
        request.context["cmd_entry_enable"] = False
        raise PostgresException(Error=str(e), DbTbl="TBCALENDER" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_change_Click(request):
    sql = ""
    try:
        strDayKbn = ""
        if inpdatachk2(request) != Common.NOMAL_OK:
            return
        for intCnt1 in range(CFSC29_LBL_MAX + 1):
            if request.context[f"txt_aday{intCnt1}"] == "":
                continue
            for intCnt2 in range(31 - 1 + 1):
                if request.context[f"txt_aday{intCnt1 + intCnt2}"] != "":
                    txt_adaytp = request.context[f"txt_adaytp{intCnt1 + intCnt2}"]
                    if txt_adaytp == CFSC29_DAYKBN_WEK:
                        strDayKbn += Const.csDAYKBN_1
                    if txt_adaytp == CFSC29_DAYKBN_SAT:
                        strDayKbn += Const.csDAYKBN_2
                    if txt_adaytp == CFSC29_DAYKBN_SUN:
                        strDayKbn += Const.csDAYKBN_3
                    if txt_adaytp == CFSC29_DAYKBN_HOL:
                        strDayKbn += Const.csDAYKBN_4
                else:
                    strDayKbn += Const.csDAYKBN_9
            break
        sql += "UPDATE TBCALENDER" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "SET DAYKBN = " + Common.dbField(strDayKbn) + ","
        sql += "UDATE = SYSDATE" + ","
        sql += "UWSID = " + Common.dbField(request.cfs_ini["iniWsNo"]) + " "
        sql += "WHERE YMDATE = " + Common.dbField(request.contextp["txt_ayear"] + "/" & request.contextp["txt_amonth"])
        with transaction.atomic():
            Common.SqlExecute(sql).execute()
        init_form(request, CFSC29_MODE0)
        request.context["gSetField"] = "txt_ayear"
    except Exception as e:
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise PostgresException(Error=str(e), DbTbl="TBCALENDER" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_delete_Click(request):
    sql = ""
    try:
        sql = "DELETE FROM TBCALENDER" + request.cfs_ini["iniUpdTbl"] + " "
        sql = sql + "WHERE YMDATE = " + Common.dbField(
            request.context["txt_ayear"] + "/" + request.context["txt_amonth"])
        with transaction.atomic():
            Common.SqlExecute(sql).execute()
        init_form(request, CFSC29_MODE0)
        request.context["gSetField"] = "txt_ayear"
    except Exception as e:
        request.context["cmd_change_enable"] = False
        request.context["cmd_delete_enable"] = False
        raise PostgresException(Error=str(e), DbTbl="TBCALENDER" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = False
    request.context["cmd_change_enable"] = False
    request.context["cmd_delete_enable"] = False

    init_form(request, CFSC29_MODE0)
    request.context["gSetField"] = "txt_ayear"


def init_form(request, intMode):
    if intMode == CFSC29_MODE0:
        request.context["txt_ayear"] = ""
        request.context["txt_amonth"] = ""
    for intCnt in range(CFSC29_LBL_MAX + 1):
        request.context[f"txt_aday{intCnt}_Caption"] = ""
        request.context[f"txt_aday{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_WEK
        request.context[f"txt_aday{intCnt}_Enabled"] = True
        request.context[f"txt_adaytp{intCnt}_Caption"] = ""
        request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_WEK
        request.context[f"txt_adaytp{intCnt}_Enabled"] = True


def inpdatachk1(request):
    if not request.context["txt_ayear"]:
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "年を入力して下さい。")
        request.context["gSetField"] = "txt_ayear"
        return Const.FATAL_ERR
    if not request.context["txt_amonth"]:
        MsgDspError(request, Const.MSG_DSP_WARN, "必須入力エラー", "月を入力して下さい。")
        request.context["gSetField"] = "txt_amonth"
        return Const.FATAL_ERR
    return Const.NOMAL_OK


def inpdatachk2(request):
    return Const.NOMAL_OK


def HolidaySet_proc(request):
    intCntWeek = 0

    txt_amonth = f"{request.context['txt_amonth']:01}"
    if txt_amonth == 1:
        for intCnt in range(CFSC29_LBL_MAX + 1):
            txt_aday = request.context[f"txt_aday{intCnt}"]
            if txt_aday == 1:
                request.context[f"txt_adaytp{intCnt}_Caption"] = CFSC29_DAYKBN_HOL
                request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                request.context[f"txt_aday{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                break
        for intCnt in range(1, CFSC29_LBL_MAX + 1, 7):
            if request.context[f"txt_aday{intCnt}"] != "":
                intCntWeek += 1
            if intCntWeek == 2:
                request.context[f"txt_adaytp{intCnt}_Caption"] = CFSC29_DAYKBN_HOL
                request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                request.context[f"txt_aday{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                break
    elif txt_amonth == 2:
        for intCnt in range(CFSC29_LBL_MAX + 1):
            txt_aday = request.context[f"txt_aday{intCnt}"]
            if txt_aday == 11:
                request.context[f"txt_adaytp{intCnt}_Caption"] = CFSC29_DAYKBN_HOL
                request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                request.context[f"txt_aday{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                break
