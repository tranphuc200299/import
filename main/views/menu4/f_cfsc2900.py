import calendar
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
CFSC29_LBL_MAX = 42
CFSC29_DAYKBN_OUT_BOUND = ""
CFSC29_DAYKBN_WEK = ""
CFSC29_DAYKBN_SAT = "土曜"
CFSC29_DAYKBN_SUN = "日曜"
CFSC29_DAYKBN_HOL = "祝日"
CFSC29_DAYKBN_COL_OUT_BOUND = "#BBBBC3"
CFSC29_DAYKBN_COL_WEK = "#FFFFFF"
CFSC29_DAYKBN_COL_SAT = "#BFCEF2"
CFSC29_DAYKBN_COL_SUN = "#FAC5CB"
CFSC29_DAYKBN_COL_HOL = "#FE98A3"
CFSC29_DAYKBN_TEXT_IN_MONTH_COL = "#000000"
CFSC29_DAYKBN_TEXT_OUT_MONTH_COL = "#FFFFFF"
CFSC29_YEAR_MIN = 1
CFSC29_YEAR_MAX = 12


@update_context()
@load_cfs_ini("menu4")
def f_cfsc2900(request):
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
            for i in range(CFSC29_LBL_MAX):
                if action == f"txt_adaytp{i}":
                    txt_adaytp_Click(request, i)
                    break
    else:
        Form_Load(request)
    return render(request, "menu/menu4/f_cfsc2900.html", request.context)


def Form_Load(request):
    init_form(request, CFSC29_MODE0)
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"


def txt_ayear_LostFocus(request):
    if request.context["txt_ayear"]:
        if not Common.IsNumeric(request.context["txt_ayear"]):
            MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー", "年は整数(9999形式)で入力して下さい。")
            request.context["gSetField"] = "txt_ayear"
            return ["gSetField", "MsgDsp"]
        request.context["txt_ayear"] = f"{int(request.context['txt_ayear']):04}"
    return "txt_ayear"


def txt_amonth_LostFocus(request):
    if request.context["txt_amonth"]:
        if not Common.IsNumeric(request.context["txt_amonth"]):
            MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー", "月は整数(99形式)で入力して下さい。")
            request.context["gSetField"] = "txt_amonth"
            return ["gSetField", "MsgDsp"]
        if CFSC29_YEAR_MIN > int(request.context["txt_amonth"]) or CFSC29_YEAR_MAX < int(request.context["txt_amonth"]):
            MsgDspError(request, Const.MSG_DSP_WARN, "入力整合性エラー",
                        "年は" + CFSC29_YEAR_MIN + "から" + CFSC29_YEAR_MAX + "以内で入力して下さい。")
            request.context["gSetField"] = "txt_amonth"
            return ["gSetField", "MsgDsp"]
        request.context["txt_amonth"] = f"{int(request.context['txt_amonth']):02}"
    return "txt_amonth"


def txt_adaytp_Click(request, index):
    txt_adaytp = request.context[f"txt_adaytp{index}_DateText"]
    if txt_adaytp == CFSC29_DAYKBN_WEK:
        request.context[f"txt_adaytp{index}_DateText"] = CFSC29_DAYKBN_SAT
        request.context[f"txt_adaytp{index}_BackColor"] = CFSC29_DAYKBN_COL_SAT
    elif txt_adaytp == CFSC29_DAYKBN_SAT:
        request.context[f"txt_adaytp{index}_DateText"] = CFSC29_DAYKBN_SUN
        request.context[f"txt_adaytp{index}_BackColor"] = CFSC29_DAYKBN_COL_SUN
    elif txt_adaytp == CFSC29_DAYKBN_SUN:
        request.context[f"txt_adaytp{index}_DateText"] = CFSC29_DAYKBN_HOL
        request.context[f"txt_adaytp{index}_BackColor"] = CFSC29_DAYKBN_COL_HOL
    elif txt_adaytp == CFSC29_DAYKBN_HOL:
        request.context[f"txt_adaytp{index}_DateText"] = CFSC29_DAYKBN_WEK
        request.context[f"txt_adaytp{index}_BackColor"] = CFSC29_DAYKBN_COL_WEK


def txt_ayear_Change(request):
    request.context["txt_ayear"] = request.context["txt_ayear"].upper()
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"
    return ["txt_ayear", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def txt_amonth_Change(request):
    request.context["txt_amonth"] = request.context["txt_amonth"].upper()
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"
    return ["txt_amonth", "cmd_entry_enable", "cmd_change_enable", "cmd_delete_enable"]


def cmd_search_Click(request):
    sql = ""
    try:
        init_form(request, CFSC29_MODE1)
        if inpdatachk1(request) != Const.NOMAL_OK:
            return

        intStrLbl = __get_name_day_of_first_month(request)
        total_date_current_month = \
            calendar.monthrange(int(request.context["txt_ayear"]), int(request.context["txt_amonth"]))[1]

        if int(request.context["txt_amonth"]) == 1:
            total_date_previous_month = calendar.monthrange(int(request.context["txt_ayear"]) - 1, 12)[1]
        else:
            total_date_previous_month = \
                calendar.monthrange(int(request.context["txt_ayear"]), int(request.context["txt_amonth"]) - 1)[1]

        sql += "SELECT * "
        sql += "FROM TBCALENDER" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "WHERE YMDATE = " + Common.dbField(request.context["txt_ayear"] + "/" + request.context["txt_amonth"])
        sql += " FOR UPDATE NOWAIT"
        RsTbCalender = Common.SqlExecute(sql).all()

        # get day in previous month
        total_date_need_of_month_before = intStrLbl
        reversed_index = total_date_need_of_month_before
        for i in range(total_date_need_of_month_before):
            request.context[f"txt_adaytp{i}_DateNum"] = total_date_previous_month - reversed_index + 1
            request.context[f"txt_adaytp{i}_DateText"] = CFSC29_DAYKBN_OUT_BOUND
            request.context[f"txt_adaytp{i}_BackColor"] = CFSC29_DAYKBN_COL_OUT_BOUND
            request.context[f"txt_adaytp{i}_Enabled"] = "False"
            request.context[f"txt_adaytp{i}_TextColor"] = CFSC29_DAYKBN_TEXT_OUT_MONTH_COL
            reversed_index -= 1

        # get day in next month
        total_date_need_of_month_after = intStrLbl + total_date_current_month
        increase_index = 1
        for i in range(total_date_need_of_month_after, CFSC29_LBL_MAX):
            request.context[f"txt_adaytp{i}_DateNum"] = increase_index
            request.context[f"txt_adaytp{i}_DateText"] = CFSC29_DAYKBN_OUT_BOUND
            request.context[f"txt_adaytp{i}_BackColor"] = CFSC29_DAYKBN_COL_OUT_BOUND
            request.context[f"txt_adaytp{i}_Enabled"] = "False"
            request.context[f"txt_adaytp{i}_TextColor"] = CFSC29_DAYKBN_TEXT_OUT_MONTH_COL
            increase_index += 1

        if not RsTbCalender.Rows:
            # get day in current month
            total_date_need_of_current_month = intStrLbl + total_date_current_month
            for i in range(intStrLbl, total_date_need_of_current_month):
                if i == 0 or i % 7 == 0:
                    request.context[f"txt_adaytp{i}_DateText"] = CFSC29_DAYKBN_SUN
                    request.context[f"txt_adaytp{i}_BackColor"] = CFSC29_DAYKBN_COL_SUN
                elif i % 7 == 6:
                    request.context[f"txt_adaytp{i}_DateText"] = CFSC29_DAYKBN_SAT
                    request.context[f"txt_adaytp{i}_BackColor"] = CFSC29_DAYKBN_COL_SAT
                else:
                    request.context[f"txt_adaytp{i}_DateText"] = CFSC29_DAYKBN_WEK
                    request.context[f"txt_adaytp{i}_BackColor"] = CFSC29_DAYKBN_COL_WEK
                request.context[f"txt_adaytp{i}_ThisMonth"] = "True"
                request.context[f"txt_adaytp{i}_TextColor"] = CFSC29_DAYKBN_TEXT_IN_MONTH_COL
                request.context[f"txt_adaytp{i}_DateNum"] = i - intStrLbl + 1
                request.context[f"txt_adaytp{i}_Enabled"] = "True"
            HolidaySet_proc(request, intStrLbl, total_date_need_of_current_month)
            request.context["cmd_entry_enable"] = "True"
        else:
            strDayKbn = Common.DbDataChange(RsTbCalender.Rows[0]["daykbn"])

            range_calendar = []
            for i in range(intStrLbl, intStrLbl + total_date_current_month):
                range_calendar.append(i)
            range_strDay = []
            for strday in strDayKbn:
                range_strDay.append(strday)
            mix_data = zip(range_calendar, range_strDay)

            # get day in current month
            date_num = 1
            for data in mix_data:
                id_html = data[0]
                stype_strDay = data[1]
                if stype_strDay == Const.csDAYKBN_1:
                    request.context[f"txt_adaytp{id_html}_DateText"] = CFSC29_DAYKBN_WEK
                    request.context[f"txt_adaytp{id_html}_BackColor"] = CFSC29_DAYKBN_COL_WEK
                elif stype_strDay == Const.csDAYKBN_2:
                    request.context[f"txt_adaytp{id_html}_DateText"] = CFSC29_DAYKBN_SAT
                    request.context[f"txt_adaytp{id_html}_BackColor"] = CFSC29_DAYKBN_COL_SAT
                elif stype_strDay == Const.csDAYKBN_3:
                    request.context[f"txt_adaytp{id_html}_DateText"] = CFSC29_DAYKBN_SUN
                    request.context[f"txt_adaytp{id_html}_BackColor"] = CFSC29_DAYKBN_COL_SUN
                elif stype_strDay == Const.csDAYKBN_4:
                    request.context[f"txt_adaytp{id_html}_DateText"] = CFSC29_DAYKBN_HOL
                    request.context[f"txt_adaytp{id_html}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                elif stype_strDay == Const.csDAYKBN_9:
                    request.context[f"txt_adaytp{id_html}_DateText"] = CFSC29_DAYKBN_OUT_BOUND
                    request.context[f"txt_adaytp{id_html}_BackColor"] = CFSC29_DAYKBN_COL_OUT_BOUND
                request.context[f"txt_adaytp{id_html}_ThisMonth"] = "True"
                request.context[f"txt_adaytp{id_html}_TextColor"] = CFSC29_DAYKBN_TEXT_IN_MONTH_COL
                request.context[f"txt_adaytp{id_html}_DateNum"] = date_num
                request.context[f"txt_adaytp{id_html}_Enabled"] = "True"
                date_num += 1
            request.context["cmd_change_enable"] = "True"
            request.context["cmd_delete_enable"] = "True"
    except Exception as e:
        raise PostgresException(Error=str(e), DbTbl="TBCALENDER" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_entry_Click(request):
    sql = ""
    try:
        strDayKbn = ""
        if inpdatachk2(request) != Common.NOMAL_OK:
            return

        intStrLbl = __get_name_day_of_first_month(request)
        for i in range(intStrLbl, intStrLbl + 31):
            txt_adaytp = request.context[f"txt_adaytp{i}_DateText"]
            if txt_adaytp == CFSC29_DAYKBN_WEK:
                strDayKbn += Const.csDAYKBN_1
            elif txt_adaytp == CFSC29_DAYKBN_SAT:
                strDayKbn += Const.csDAYKBN_2
            elif txt_adaytp == CFSC29_DAYKBN_SUN:
                strDayKbn += Const.csDAYKBN_3
            elif txt_adaytp == CFSC29_DAYKBN_HOL:
                strDayKbn += Const.csDAYKBN_4

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
        request.context["cmd_entry_enable"] = "False"
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
    except Exception as e:
        request.context["cmd_entry_enable"] = False
        raise PostgresException(Error=str(e), DbTbl="TBCALENDER" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_change_Click(request):
    sql = ""
    try:
        strDayKbn = ""
        if inpdatachk2(request) != Common.NOMAL_OK:
            return

        intStrLbl = __get_name_day_of_first_month(request)
        for i in range(intStrLbl, intStrLbl + 31):
            txt_adaytp = request.context[f"txt_adaytp{i}_DateText"]
            if txt_adaytp == CFSC29_DAYKBN_WEK:
                strDayKbn += Const.csDAYKBN_1
            elif txt_adaytp == CFSC29_DAYKBN_SAT:
                strDayKbn += Const.csDAYKBN_2
            elif txt_adaytp == CFSC29_DAYKBN_SUN:
                strDayKbn += Const.csDAYKBN_3
            elif txt_adaytp == CFSC29_DAYKBN_HOL:
                strDayKbn += Const.csDAYKBN_4
            else:
                strDayKbn += Const.csDAYKBN_9

        sql += "UPDATE TBCALENDER" + request.cfs_ini["iniUpdTbl"] + " "
        sql += "SET DAYKBN = " + Common.dbField(strDayKbn) + ","
        sql += "UDATE = CURRENT_TIMESTAMP" + ","
        sql += "UWSID = " + Common.dbField(request.cfs_ini["iniWsNo"]) + " "
        sql += "WHERE YMDATE = " + Common.dbField(request.context["txt_ayear"] + "/" + request.context["txt_amonth"])
        with transaction.atomic():
            Common.SqlExecute(sql).execute()
        init_form(request, CFSC29_MODE0)
        request.context["gSetField"] = "txt_ayear"
        request.context["cmd_entry_enable"] = "False"
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
    except Exception as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
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
        request.context["cmd_entry_enable"] = "False"
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
    except Exception as e:
        request.context["cmd_change_enable"] = "False"
        request.context["cmd_delete_enable"] = "False"
        raise PostgresException(Error=str(e), DbTbl="TBCALENDER" + request.cfs_ini["iniUpdTbl"], SqlStr=sql)


def cmd_cancel_Click(request):
    request.context["cmd_entry_enable"] = "False"
    request.context["cmd_change_enable"] = "False"
    request.context["cmd_delete_enable"] = "False"

    init_form(request, CFSC29_MODE0)
    request.context["gSetField"] = "txt_ayear"


def init_form(request, intMode):
    if intMode == CFSC29_MODE0:
        request.context["txt_ayear"] = ""
        request.context["txt_amonth"] = ""
    for intCnt in range(CFSC29_LBL_MAX):
        request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_WEK
        request.context[f"txt_adaytp{intCnt}_DateNum"] = ""
        request.context[f"txt_adaytp{intCnt}_DateText"] = ""
        request.context[f"txt_adaytp{intCnt}_Enabled"] = "False"
        request.context[f"txt_adaytp{intCnt}_ThisMonth"] = "False"


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


def HolidaySet_proc(request, intStrLbl, total_date_need_of_current_month):
    txt_amonth = int(f"{int(request.context['txt_amonth']):01}")
    date_range = range(intStrLbl, total_date_need_of_current_month)
    if txt_amonth == 1:
        for index, intCnt in enumerate(date_range):
            # 1/元旦, 第２月曜 / 成人の日
            if index in [0, 8]:
                request.context[f"txt_adaytp{intCnt}_DateText"] = CFSC29_DAYKBN_HOL
                request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                if index == 8:
                    break
    elif txt_amonth == 2:
        for index, intCnt in enumerate(date_range):
            # 11/建国記念日
            if index == 10:
                request.context[f"txt_adaytp{intCnt}_DateText"] = CFSC29_DAYKBN_HOL
                request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                break
    elif txt_amonth == 3:
        # 20/春分の日
        txt_ayear = int(f"{int(request.context['txt_ayear']):04}")
        if txt_ayear % 4 in [0, 1]:
            for index, intCnt in enumerate(date_range):
                if index == 19:
                    request.context[f"txt_adaytp{intCnt}_DateText"] = CFSC29_DAYKBN_HOL
                    request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                    break
        # 21/春分の日
        if txt_ayear % 4 in [2, 3]:
            for index, intCnt in enumerate(date_range):
                if index == 20:
                    request.context[f"txt_adaytp{intCnt}_DateText"] = CFSC29_DAYKBN_HOL
                    request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                    break
    elif txt_amonth == 4:
        # 29/みどりの日
        for index, intCnt in enumerate(date_range):
            if index == 28:
                request.context[f"txt_adaytp{intCnt}_DateText"] = CFSC29_DAYKBN_HOL
                request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                break
    elif txt_amonth == 5:
        # 3/憲法記念日,4/国民の休日,5/こどもの日
        for index, intCnt in enumerate(date_range):
            if index in [2, 3, 4]:
                request.context[f"txt_adaytp{intCnt}_DateText"] = CFSC29_DAYKBN_HOL
                request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                if index == 4:
                    break
    elif txt_amonth == 6:
        pass
    elif txt_amonth == 7:
        # 20/海の日
        for index, intCnt in enumerate(date_range):
            if index == 20:
                request.context[f"txt_adaytp{intCnt}_DateText"] = CFSC29_DAYKBN_HOL
                request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
    elif txt_amonth == 8:
        pass
    elif txt_amonth == 9:
        # 15/敬老の日,23/秋分の日
        for index, intCnt in enumerate(date_range):
            if index in [14, 22]:
                request.context[f"txt_adaytp{intCnt}_DateText"] = CFSC29_DAYKBN_HOL
                request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                if index == 22:
                    break
    elif txt_amonth == 10:
        # 第２月曜/体育の日
        for index, intCnt in enumerate(date_range):
            if index == 8:
                request.context[f"txt_adaytp{intCnt}_DateText"] = CFSC29_DAYKBN_HOL
                request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
    elif txt_amonth == 11:
        # 3/文化の日,23/勤労感謝の日
        for index, intCnt in enumerate(date_range):
            if index in [2, 22]:
                request.context[f"txt_adaytp{intCnt}_DateText"] = CFSC29_DAYKBN_HOL
                request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL
                if index == 22:
                    break
    elif txt_amonth == 12:
        # 第２月曜/体育の日
        for index, intCnt in enumerate(date_range):
            if index == 22:
                request.context[f"txt_adaytp{intCnt}_DateText"] = CFSC29_DAYKBN_HOL
                request.context[f"txt_adaytp{intCnt}_BackColor"] = CFSC29_DAYKBN_COL_HOL


def __get_name_day_of_first_month(request):
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
    return intStrLbl
