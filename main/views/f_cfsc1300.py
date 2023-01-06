import logging
from main.common.decorators import update_context
from main.common.constants import *
from django.shortcuts import redirect, render
from django.db import IntegrityError, transaction

from main.common.function import SqlExecute

_logger = logging.getLogger(__name__)
PROGID = 'cfsm1300'
CFSC13_MODE0 = 0
CFSC13_MODE1 = 1
intDbLock = 0
@update_context()
def f_cfsc1300(request):
    request.context["gSetField"] = "txtKadoYm"
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "btnFind":
            cmd_search_Click(request)
        elif action == "btnInsert":
            cmd_entry_Click(request)
        elif action == "btnUpdate":
            cmd_change_Click(request)
        elif action == "btnClear":
            cmd_cancel_Click(request)
        elif action == "btnDelete":
            return cmd_delete_Click(request)
    else:
    #     if request.GET.get("action") == "reloadDataList":
    #         return grdDataListCommon(request, "carTOpeCarFind")
    #     else:
    #         if request.GET.get('mode', False):
        Form_Load(request)
    #             Set_Screen(request, "carTOpeCarFind")
    return render(request, "f_cfsc1300.html", request.context)

def Form_Load(request):
    global intDbLock
    intDbLock = 0
    init_form(CFSC13_MODE0)

    request.context["cmd_entry"] = "False"
    request.context["cmd_change"] = "False"
    request.context["cmd_delete"] = "False"

    request.context["lbl_aSelHozNam"] = request.context["strSelHozNam"]

    request.context["strProcHozCd"] = request.context["strSelHozCd"]
    request.context["strProcHozNam"] = request.context["strSelHozNam"]
    request.context["strProcTbl"] = request.context["strSelTbl"]

def txt_afwdcd_Change(request):
    request.context["txt_afwdcd"] = request.context["txt_afwdcd"].upper()
    request.context["cmd_entry"] = "False"
    request.context["cmd_change"] = "False"
    request.context["cmd_delete"] = "False"
    global intDbLock
    if intDbLock == 1:

        intDbLock = 0


def init_form(request, intMode):
    if intMode == CFSC13_MODE0:
        request.context["txt_afwdcd"] = ""
    request.context["txt_afwdnm"] = ""
    request.context["txt_afwdtannm"] = ""
    request.context["txt_afwdtel"] = ""
    request.context["txt_afwdfax"] = ""
def cmd_search_Click(request):
    init_form(CFSC13_MODE1)
    if inpdatachk1 != NOMAL_OK:
        return
    sql = 'SELECT * '
    sql += 'FROM TBFORWARD' + request.context["strProcTbl.Text"] + ' '
    sql += 'WHERE FWDCD = ' + request.context["txt_afwdcd.Text"]
    sql += ' FOR UPDATE NOWAIT'

    RsTbForward = SqlExecute(sql).all()
    intDbLock = 1
    if not RsTbForward.Rows:
        request.context["cmd_entry"]= "True"
    else:
        request.context["txt_afwdnm.Text"] = DbDataChange(RsTbForward.Rows[0]["FWDNM"])
        request.context["txt_afwdtannm.Text"] = DbDataChange(RsTbForward.Rows[0]["FWDTANNM"])
        request.context["txt_afwdtel.Text"] = DbDataChange(RsTbForward.Rows[0]["FWDTEL"])
        request.context["txt_afwdfax.Text"] = DbDataChange(RsTbForward.Rows[0]["FWDFAX"])
        request.context["cmd_change"]= "True"
        request.context["cmd_delete"]= "True"
    RsTbForward = None
    request.context["gSetField"] = "txt_afwdnm"
    return

def cmd_entry_Click(request):

    if inpdatachk2(request) != NOMAL_OK :
        return

    sql = 'INSERT INTO TBFORWARD' + request.context["strProcTbl.Text"] + ' '
    sql += '(FWDCD,FWDNM,FWDTANNM,FWDTEL,FWDFAX,UDATE,UWSID) '
    sql += 'VALUES('
    sql += request.context["txt_afwdcd.Text"] + ','
    sql += request.context["txt_afwdnm.Text"] + ','
    sql += request.context["txt_afwdtannm.Text"] + ','
    sql += request.context["txt_afwdtel.Text"] + ','
    sql += request.context["txt_afwdfax.Text"] + ','
    sql += 'CURRENT_TIMESTAMP' + ','
    sql += request.context["iniWsNo"] + ')'

    try:
        with transaction.atomic():
            SqlExecute(sql).execute()
            global intDbLock
            intDbLock = 0
            init_form(CFSC13_MODE0)
            request.context["gSetField"] = "txt_afwdcd"
    except IntegrityError as ie:
        _logger.error(ie)
        intDbLock = 0
        request.context["cmd_entry"] = "False"

def cmd_change_Click(request):
    sql = 'UPDATE TBFORWARD' + request.context["strProcTbl.Text"] + ' '

    sql += 'SET FWDNM = ' + request.context["txt_afwdnm.Text"] + ','
    sql += 'FWDTANNM = ' + request.context["txt_afwdtannm.Text"] + ','
    sql += 'FWDTEL = ' + request.context["txt_afwdtel.Text"] + ','
    sql += 'FWDFAX = ' + request.context["txt_afwdfax.Text"] + ','
    sql += 'UDATE = SYSDATE' + ','
    sql += 'UWSID = ' + request.context["iniWsNo"] + ' '
    # WHERE部
    sql += 'WHERE FWDCD = ' + request.context["txt_afwdcd.Text"]

    try:
        with transaction.atomic():
            SqlExecute(sql).execute()
            global intDbLock
            intDbLock = 0
            init_form(CFSC13_MODE0)
            request.context["gSetField"] = "txt_afwdcd"
    except IntegrityError as ie:
        _logger.error(ie)
        intDbLock = 0
        request.context["cmd_change"] = "False"
        request.context["cmd_delete"] = "False"


def cmd_delete_Click(request):
    sql = 'DELETE FROM TBFORWARD' + request.context["strProcTbl"] + ' '
    sql += 'WHERE FWDCD = ' + request.context["txt_afwdcd"]
    try:
        with transaction.atomic():
            SqlExecute(sql).execute()
            global intDbLock
            intDbLock = 0
            init_form(CFSC13_MODE0)
            request.context["gSetField"] = "txt_afwdcd"
    except IntegrityError as ie:
        _logger.error(ie)
        request.context["cmd_change"] = "False"
        request.context["cmd_delete"] = "False"


def cmd_cancel_Click(request):
    global intDbLock
    request.context["cmd_entry"] = "False"
    request.context["cmd_change"] = "False"
    request.context["cmd_delete"] = "False"
    if intDbLock == 1:
        transaction.rollback()
        intDbLock = 0
    init_form(CFSC13_MODE0)
    request.context["gSetField"] = "txt_afwdcd"


def inpdatachk1(request):
    if not request.context["txt_afwdcd"]:
        request.context["lblMsg"] = '必須入力エラー', '海貨業者コードを入力して下さい。'
        request.context["gSetField"] = "txt_afwdcd"
        fn_return_value = FATAL_ERR
        return fn_return_value
    fn_return_value = NOMAL_OK
    return fn_return_value

def inpdatachk2(request):
    if  request.context["txt_afwdnm"] == '':
        request.context["lblMsg"] = '必須入力エラー', '海貨業者名称を入力して下さい。'
        request.context["gSetField"] = "txt_afwdnm"
        fn_return_value = FATAL_ERR
        return fn_return_value
    if len(request.context["txt_afwdnm"]) > 60:
        request.context["lblMsg"] = '入力桁数エラー', '海貨業者名称は'+'60'+'桁以内で入力して下さい。'
        request.context["gSetField"] = "txt_afwdnm"
        fn_return_value = FATAL_ERR
        return fn_return_value
    if len(request.context["txt_afwdtannm"]) > 10:
        request.context["lblMsg"] = '入力桁数エラー', '海貨業者担当者名称は'+'10'+'桁以内で入力して下さい。'
        request.context["gSetField"] = "txt_afwdtannm"
        fn_return_value = FATAL_ERR
        return fn_return_value
    fn_return_value = NOMAL_OK
    return fn_return_value


def DbDataChange(DbStr):
    if not DbStr:
        fn_return_value = ''
    else:
        fn_return_value = DbStr
    return fn_return_value
