import os
from datetime import datetime
import logging
import psycopg2
from main.common.function.Const import *
from main.common.function.Common import pfncDataSessionGet, dbField, DbDataChange
from main.common.function import SqlExecute

dir_path = os.path.dirname(os.path.realpath(__file__))

_logger = logging.getLogger(__name__)


def GetArguments(EData, csArgsIN, csArgsOK, csArgsNG, WkArgs):
    try:
        WkRPos = WkArgs.index(csArgsIN)  # 受信電文ファイル先頭位置
        WkFPos = WkArgs.index(csArgsOK)  # 正常終了時ファイル先頭位置
        WkEPos = WkArgs.index(csArgsNG)  # 異常終了時ファイル先頭位置
        argNaccsFile = WkArgs[WkRPos: WkRPos + WkFPos][3].strip()
        argOKFile = WkArgs[WkFPos: WkEPos][3].strip()
        argNGFile = WkArgs[WkFPos: WkEPos + WkFPos + 1][3].strip()
        return rtnProcOK
    except Exception as Err:
        _logger.error("GetArguments: {}".format(Err))
        return rtnProcNG


def GetArguments2(EData, WkArgs, csArgsOTH1, csArgsOTH2, csArgsOTH3):
    try:
        WkPos1 = WkArgs.index(csArgsOTH1)  # 'その他引数①先頭位置
        WkPos2 = WkArgs.index(csArgsOTH2)  # 'その他引数②先頭位置
        WkPos3 = WkArgs.index(csArgsOTH3)  # 'その他引数③先頭位置
        if WkPos1 == 0:
            argStr1 = ""
        else:
            argStr1 = WkArgs[WkPos1][4].strip()
            WkPos1 = argStr1.index("-")
            if WkPos1 != 0:
                argStr1 = argStr1[:WkPos1][0].strip()
        if WkPos2 == 0:
            argStr2 = ""
        else:
            argStr2 = WkArgs[WkPos2][4].strip()
            WkPos2 = argStr1.index("-")
            if WkPos2 != 0:
                argStr2 = argStr2[:WkPos2][0].strip()

        if WkPos3 == 0:
            argStr3 = ""
        else:
            argStr3 = WkArgs[WkPos3][4].strip()
        argNaccsFile = "第一引数 : [" + argStr1 + "]"
        argOKFile = "第二引数 : [" + argStr2 + "]"
        argNGFile = "第三引数 : [" + argStr3 + "]"
        return rtnProcOK
    except Exception as Err:
        _logger.error("GetArguments2: {}".format(Err))

        return rtnProcNG


def InitNaccsBatch(request, EData, WkArgs, csArgsOTH1, csArgsOTH2, csArgsOTH3, argNaccsFile):
    try:
        if GetArguments(EData, WkArgs, csArgsOTH1, csArgsOTH2, csArgsOTH3) == rtnProcNG:
            return rtnProcNG
        iniWsNo = pfncDataSessionGet(request, "sHostnm")
        f = open(argNaccsFile, "r")
        WkFStr = f.read()
        dtNUserCd = WkFStr[29:35].strip()
        dtNGyomuCd = WkFStr[3:8].strip()
        dtNOutInfCd = WkFStr[8:16].strip()
        dtSubject = WkFStr[115:180].strip()
        dtRDTandTM = WkFStr[16:30].strip()
        SqlStr = "SELECT BIKO300 "
        SqlStr += "FROM TBNACCSPG "
        SqlStr += "WHERE "
        SqlStr += f"USERCD = {dbField(dtNUserCd)} AND "
        SqlStr += f"NOUTINFCD = {dbField(dtNOutInfCd)}"
        RsNaccs = SqlExecute(SqlStr).all()
        if not RsNaccs.Rows:
            _logger.error("InitNaccsBatch: errOraNotFound - NACCS業務プログラムテーブル該当データなし")
            return rtnProcNG
        WkBiko300 = DbDataChange(RsNaccs.Rows[0]["BIKO300"])
        strProcTbl = WkBiko300[csBiko300_001_S: csBiko300_001_M]
        return rtnProcOK
    except psycopg2.OperationalError as e:
        if e.pgcode == "2200H":
            _logger.error("InitNaccsBatch: NACCS電文{}".format(e))

        return rtnProcNG


def InitNaccsBatch2(request, EData, WkArgs, csArgsOTH1, csArgsOTH2, csArgsOTH3):
    try:
        if GetArguments2(EData, WkArgs, csArgsOTH1, csArgsOTH2, csArgsOTH3) == rtnProcNG:
            return rtnProcNG
        iniWsNo = pfncDataSessionGet(request, "sHostnm")
        return rtnProcOK
    except psycopg2.OperationalError as e:
        if e.pgcode == "2200H":
            _logger.error("InitNaccsBatch2: NACCS電文{}".format(e))
        return rtnProcNG


def ErrLogWrite(ELog, EData, dtNUserCd, dtNGyomuCd, dtNOutInfCd, dtSubject, argNaccsFile, argOKFile, argNGFile, iniWsNo):
    try:
        WkEDate = datetime.now().strftime("%Y/%m/%d")
        WkETime = datetime.now().strftime("%H:%M:%S")
        if ELog.EData.ErrCd == "" and ELog.EData.ErrData == "":
            WkEMsg = ""
        else:
            WkEMsg = ELog.EData.ErrCd + " : " + ELog.EData.ErrData
        SqlStr = "INSERT INTO TBNACCSERR("
        SqlStr += "USERCD, "
        SqlStr += "EDATE, "
        SqlStr += "ETIME, "
        SqlStr += "ETUBAN, "
        SqlStr += "ESTATUS, "
        SqlStr += "GYOMUCD, "
        SqlStr += "NOUTINFCD, "
        SqlStr += "SUBJECT, "
        SqlStr += "GYOMUDATA, "
        SqlStr += "USRERRMSG, "
        SqlStr += "SYSERRMSG, "
        SqlStr += "EPROUTKBN, "
        SqlStr += "GPROGARG1, "
        SqlStr += "GPROGARG2, "
        SqlStr += "GPROGARG3, "
        SqlStr += "ERRPLACE, "
        SqlStr += "BIKO100, "
        SqlStr += "UPROGID, "
        SqlStr += "UWSID) "
        SqlStr += "SELECT "
        SqlStr += dbField(dtNUserCd) + ", "
        SqlStr += dbField(WkEDate) + ", "
        SqlStr += dbField(WkETime) + ", "
        SqlStr += "NVL(MAX(ETUBAN),0) + 1, "
        SqlStr += dbField(ELog.EStatus) + ", "
        SqlStr += dbField(dtNGyomuCd) + ", "
        SqlStr += dbField(dtNOutInfCd) + ", "
        SqlStr += dbField(dtSubject) + ", "
        SqlStr += dbField(ELog.GData) + ", "
        SqlStr += dbField(ELog.EMsg) + ", "
        SqlStr += dbField(WkEMsg) + ", "
        SqlStr += "CHR(00), "
        SqlStr += dbField(argNaccsFile) + ", "
        SqlStr += dbField(argOKFile) + ", "
        SqlStr += dbField(argNGFile) + ", "
        SqlStr += dbField(ELog.EData.EPlace) + ", "
        SqlStr += dbField(ELog.Biko) + ", "
        SqlStr += dbField(ELog.EProgId) + ", "
        SqlStr += dbField(iniWsNo)
        SqlStr += " FROM TBNACCSERR WHERE "
        SqlStr += "USERCD = " + dbField(dtNUserCd) + " AND "
        SqlStr += "EDATE = " + dbField(WkEDate)
        SqlExecute(SqlStr).execute()
        return rtnProcOK
    except psycopg2.OperationalError as e:
        _logger.error("ErrLogWrite: {}".format(e))
        return rtnProcNG


def TbCfsSysSELECTB(UserCd, SysData, LockKbn, strProcTbl):
    try:
        SqlStr = "SELECT "
        SqlStr += "HOZEICD, "
        SqlStr += "COMPANYNM, "
        SqlStr += "BRANCHNM, "
        SqlStr += "JIMUSYCD, "
        SqlStr += "JIMUSYNM, "
        SqlStr += "JIMUSYADR, "
        SqlStr += "JIMUSYTEL, "
        SqlStr += "JIMUSYFAX, "
        SqlStr += "KEIJIMSG, "
        SqlStr += "HPORTCD, "
        SqlStr += "HOZEINM, "
        SqlStr += "GWSKBN, "
        SqlStr += "GW1IP, "
        SqlStr += "GW1USERID, "
        SqlStr += "GW1PASSWD, "
        SqlStr += "GW1NAME, "
        SqlStr += "GW1SDIR, "
        SqlStr += "GW2IP, "
        SqlStr += "GW2USERID, "
        SqlStr += "GW2PASSWD, "
        SqlStr += "GW2NAME, "
        SqlStr += "GW2SDIR, "
        SqlStr += "USERCD, "
        SqlStr += "IDCD1, "
        SqlStr += "USERPSWD1, "
        SqlStr += "IDCD2, "
        SqlStr += "USERPSWD2, "
        SqlStr += "IOJNOHEAD, "
        SqlStr += "IOJNOMIN, "
        SqlStr += "IOJNOMAX, "
        SqlStr += "IOJNONOW, "
        SqlStr += "UNQFILENM, "
        SqlStr += "TAXNEW, "
        SqlStr += "TAXOLD, "
        SqlStr += "TAXCHG, "
        SqlStr += "GENGONEW, "
        SqlStr += "GENGOOLD, "
        SqlStr += "GENGOCHG, "
        SqlStr += "SEIKYUHNO "
        SqlStr += f"FROM TBCFSSYS{strProcTbl}"
        SqlStr += " WHERE "
        SqlStr += f"USERCD = {dbField(UserCd)}"
        if LockKbn == csLOCK_ON:
            SqlStr += " FOR UPDATE NOWAIT"
        RsSys = SqlExecute(SqlStr).all()
        if not RsSys.Rows:
            return rtnProcNF
        SysData.HOZEICD = DbDataChange(RsSys.Rows[0]["HOZEICD"])
        SysData.COMPANYNM = DbDataChange(RsSys.Rows[0]["COMPANYNM"])
        SysData.BRANCHNM = DbDataChange(RsSys.Rows[0]["BRANCHNM"])
        SysData.JIMUSYCD = DbDataChange(RsSys.Rows[0]["JIMUSYCD"])
        SysData.JIMUSYNM = DbDataChange(RsSys.Rows[0]["JIMUSYNM"])
        SysData.JIMUSYADR = DbDataChange(RsSys.Rows[0]["JIMUSYADR"])
        SysData.JIMUSYTEL = DbDataChange(RsSys.Rows[0]["JIMUSYTEL"])
        SysData.JIMUSYFAX = DbDataChange(RsSys.Rows[0]["JIMUSYFAX"])
        SysData.KEIJIMSG = DbDataChange(RsSys.Rows[0]["KEIJIMSG"])
        SysData.HPORTCD = DbDataChange(RsSys.Rows[0]["HPORTCD"])
        SysData.HOZEINM = DbDataChange(RsSys.Rows[0]["HOZEINM"])
        SysData.GWSKBN = DbDataChange(RsSys.Rows[0]["GWSKBN"])
        SysData.GW1IP = DbDataChange(RsSys.Rows[0]["GW1IP"])
        SysData.GW1USERID = DbDataChange(RsSys.Rows[0]["GW1USERID"])
        SysData.GW1PASSWD = DbDataChange(RsSys.Rows[0]["GW1PASSWD"])
        SysData.GW1NAME = DbDataChange(RsSys.Rows[0]["GW1NAME"])
        SysData.GW1SDIR = DbDataChange(RsSys.Rows[0]["GW1SDIR"])
        SysData.GW2IP = DbDataChange(RsSys.Rows[0]["GW2IP"])
        SysData.GW2USERID = DbDataChange(RsSys.Rows[0]["GW2USERID"])
        SysData.GW2PASSWD = DbDataChange(RsSys.Rows[0]["GW2PASSWD"])
        SysData.GW2NAME = DbDataChange(RsSys.Rows[0]["GW2NAME"])
        SysData.GW2SDIR = DbDataChange(RsSys.Rows[0]["GW2SDIR"])
        SysData.UserCd = DbDataChange(RsSys.Rows[0]["UserCd"])
        SysData.IDCD1 = DbDataChange(RsSys.Rows[0]["IDCD1"])
        SysData.USERPSWD1 = DbDataChange(RsSys.Rows[0]["USERPSWD1"])
        SysData.IDCD2 = DbDataChange(RsSys.Rows[0]["IDCD2"])
        SysData.USERPSWD2 = DbDataChange(RsSys.Rows[0]["USERPSWD2"])
        SysData.IOJNOHEAD = DbDataChange(RsSys.Rows[0]["IOJNOHEAD"])
        SysData.IOJNOMIN = DbDataChange(RsSys.Rows[0]["IOJNOMIN"])
        SysData.IOJNOMAX = DbDataChange(RsSys.Rows[0]["IOJNOMAX"])
        SysData.IOJNONOW = DbDataChange(RsSys.Rows[0]["IOJNONOW"])
        SysData.UNQFILENM = DbDataChange(RsSys.Rows[0]["UNQFILENM"])
        SysData.TAXNEW = DbDataChange(RsSys.Rows[0]["TAXNEW"])
        SysData.TAXOLD = DbDataChange(RsSys.Rows[0]["TAXOLD"])
        SysData.TAXCHG = DbDataChange(RsSys.Rows[0]["TAXCHG"])
        SysData.GENGONEW = DbDataChange(RsSys.Rows[0]["GENGONEW"])
        SysData.GENGOOLD = DbDataChange(RsSys.Rows[0]["GENGOOLD"])
        SysData.GENGOCHG = DbDataChange(RsSys.Rows[0]["GENGOCHG"])
        SysData.SEIKYUHNO = DbDataChange(RsSys.Rows[0]["SEIKYUHNO"])
        return rtnProcOK
    except psycopg2.OperationalError as e:
        if e.pgcode == "55P03":
            return rtnOraLock
        else:
            return rtnProcNG
