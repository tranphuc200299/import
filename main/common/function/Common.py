import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from main.common.function import SqlExecute
from django.db import IntegrityError
from main.common.function.Const import DB_NOT_FIND, DB_NOMAL_OK, DB_FATAL_ERR, DB_TBFREETM_NOT_FIND, \
    DB_TBCALENDER_NOT_FIND, \
    csFKISANKBN_1, csFCALC_1, csFCALC_3, csDAYKBN_2, csDAYKBN_3, csDAYKBN_4, csDAYKBN_9

_logger = logging.getLogger(__name__)


def CmfDateFmt(rstrDate: str, input_format="%Y/%m/%d", output_format="%Y/%m/%d") -> str:
    # rintmode=2 ==> input_format="%Y-%m-%d", output_format="%Y/%m/%d"
    # rintmode=4 ==> input_format="%Y-%m-%d %H:%M:%S", output_format="%Y/%m/%d %H:%M:%S"
    try:
        return datetime.strptime(rstrDate, input_format).strftime(output_format)
    except Exception as e:
        _logger.error(e)
        return ""


def ValidChr(strIn: int) -> bool:
    strValid = "1234567890 ABCDEFGHIJKLMNOPQRSTUVWXYZ-/.()"
    strIn = chr(strIn).upper()
    if ord(strIn) > 26 and strIn not in strValid:
        return True
    return False


def ValidNumber(strIn: int) -> bool:
    strValid = "1234567890-+.,"
    strIn = chr(strIn).upper()
    if ord(strIn) > 26 and strIn not in strValid:
        return True
    return False


def ValidNumber2(strIn: int) -> bool:
    strValid = "1234567890"
    strIn = chr(strIn).upper()
    if ord(strIn) > 26 and strIn not in strValid:
        return True
    return False


def ValidDate(strIn: int) -> bool:
    strValid = "1234567890/:"
    strIn = chr(strIn).upper()
    if ord(strIn) > 26 and strIn not in strValid:
        return True
    return False


def dbField(strIn: str) -> str:
    strIn = strIn.replace("'", "''")
    if strIn == "":
        return "Chr(00)"
    else:
        return "'" + strIn + "'"


def dbsingle(strIn: str) -> float:
    if strIn == "":
        return 0
    else:
        return float(strIn.replace(",", ""))


def IsNumeric(obj):
    try:
        float(obj.replace(",", ""))
        return True
    except Exception:
        return False


def KijyunM3(objRsStani, strM3):
    if objRsStani.Rows and strM3 != "" and objRsStani.Fields("SYUBTKBN") != "2":
        if not objRsStani.Rows[0]("CONVERT"):
            dblConv = 0
        else:
            dblConv = float(objRsStani.Rows[0]["CONVERT"].replace(",", ""))
        if IsNumeric(strM3.lstrip()):
            return dbsingle(strM3.lstrip()) * dblConv
    return 0


def KijyunWt(objRsStani, strWeight):
    if objRsStani.Rows and strWeight != "" and objRsStani.Fields("SYUBTKBN") != "1":
        if not objRsStani.Rows[0]("CONVERT"):
            dblConv = 0
        else:
            dblConv = float(objRsStani.Rows[0]["CONVERT"].replace(",", ""))
        if IsNumeric(strWeight.lstrip()):
            return dbsingle(strWeight.lstrip()) * dblConv
    return 0


def CompRynTon(strM3: str) -> float:
    if IsNumeric(strM3.lstrip()):
        return dbsingle(strM3.lstrip())
    return 0


def MakeNaBlNo(objRsOpe, strCtBl):
    strDelChr = [""] * 3
    strDelLen = [0] * 3
    if strCtBl[:6] == "KKLUSH":
        return strCtBl
    if objRsOpe.Rows and strCtBl != "":
        if objRsOpe.Rows[0]["DELCHR1"] != chr(0):
            strDelChr[0] = objRsOpe.Rows[0]["DELCHR1"]
        if objRsOpe.Rows[0]["DELCHR2"] != chr(0):
            strDelChr[1] = objRsOpe.Rows[0]["DELCHR2"]
        if objRsOpe.Rows[0]["DELCHR3"] != chr(0):
            strDelChr[2] = objRsOpe.Rows[0]["DELCHR3"]
        if objRsOpe.Rows[0]["DELLEN1"] != chr(0):
            strDelLen[0] = objRsOpe.Rows[0]["DELLEN1"]
        if objRsOpe.Rows[0]["DELLEN2"] != chr(0):
            strDelLen[1] = objRsOpe.Rows[0]["DELLEN2"]
        if objRsOpe.Rows[0]["DELLEN3"] != chr(0):
            strDelLen[2] = objRsOpe.Rows[0]["DELLEN3"]
        if not objRsOpe.Rows[0]["SCACCD"]:
            strScac = ""
        else:
            strScac = objRsOpe.Rows[0]["SCACCD"]
        if not objRsOpe.Rows[0]["NSCACFLG"]:
            strNscacflg = ""
        else:
            strNscacflg = objRsOpe.Rows[0]["NSCACFLG"]

        if strDelLen[0] > 0:
            while True:
                try:
                    intBlLen = len(strCtBl)
                    intPtr = strCtBl.index(strDelChr[0])
                    strAns = strCtBl[:intPtr]
                    strCtBl = strAns + strCtBl[(intPtr - 1 + strDelLen[0]) - intBlLen:]
                except:
                    break
        if strDelLen[1] > 0:
            while True:
                try:
                    intBlLen = len(strCtBl)
                    intPtr = strCtBl.index(strDelChr[1])
                    strAns = strCtBl[:intPtr]
                    strCtBl = strAns + strCtBl[(intPtr - 1 + strDelLen[1]) - intBlLen:]
                except:
                    break
        if strDelLen[2] > 0:
            while True:
                try:
                    intBlLen = len(strCtBl)
                    intPtr = strCtBl.index(strDelChr[2])
                    strAns = strCtBl[:intPtr]
                    strCtBl = strAns + strCtBl[(intPtr - 1 + strDelLen[2]) - intBlLen:]
                except:
                    break
        if strNscacflg == "y" or strNscacflg == "Y":
            return strScac + strCtBl
        return strCtBl


def GetFreeTime(OpeCd, AreaCd, KDate, strSelTbl):
    try:
        WkErrTbl = "フリータイムテーブル"
        SqlStr = f"SELECT FKISANKBN, FDAYS, FCALC FROM TBFREETM{strSelTbl} WHERE "
        SqlStr += f"OPECD = {dbField(OpeCd)} AND "
        SqlStr += f"FREEKBN = {dbField(AreaCd)}"
        RsFreeTm = SqlExecute(SqlStr).all()
        if not RsFreeTm.Rows:
            return DB_TBFREETM_NOT_FIND
        WkFKISANKBN = RsFreeTm.Rows[0]["FKISANKBN"]
        WkFDAYS = int(RsFreeTm.Rows[0]["FDAYS"]) - 1
        WkFCALC = RsFreeTm.Rows[0]["FCALC"]
        WkErrTbl = "カレンダーテーブル"
        SqlStr = f"SELECT YMDATE, DAYKBN FROM TBCALENDER{strSelTbl} WHERE "
        SqlStr += f"YMDATE >= {dbField(CmfDateFmt(KDate, output_format='%Y/%m'))}"
        SqlStr += " ORDER BY YMDATE"
        if not RsFreeTm.Rows:
            return DB_TBCALENDER_NOT_FIND
        tbcalen = []
        for i in range(len(RsFreeTm.Rows)):
            tbcalen.append({
                "YMDATE": RsFreeTm.Rows[i]["YMDATE"],
                "YMDATEY": int(RsFreeTm.Rows[i]["YMDATE"][0:4]),
                "YMDATEM": int(RsFreeTm.Rows[i]["YMDATE"][6:8]),
                "DAYKBN": RsFreeTm.Rows[i]["DAYKBN"]
            })
        if WkFKISANKBN == csFKISANKBN_1:
            WkKDate = KDate
        else:
            WkKDateY = CmfDateFmt((datetime.strptime(KDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
                                  "%Y")
            WkKDateM = CmfDateFmt((datetime.strptime(KDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
                                  "%m")
            WkKDateD = CmfDateFmt((datetime.strptime(KDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
                                  "%d")
            WkFreeTime = ""
            if WkFCALC == csFCALC_3:
                WkKDate = WkKDateY + "/" + WkKDateM + "/" + WkKDateD
            else:
                for i in range(len(RsFreeTm.Rows)):
                    if tbcalen[i]["YMDATE"] == WkKDateY + "/" + WkKDateM:
                        day_kbn = tbcalen[i]["DAYKBN"][int(WkKDateD) - 1]
                        if day_kbn == csDAYKBN_2:
                            if WkFCALC == csFCALC_1:
                                WkKDate = WkKDateY + "/" + WkKDateM + "/" + WkKDateD
                            else:
                                WkKDateD = int(WkKDateD) + 1
                        elif day_kbn in [csDAYKBN_3, csDAYKBN_4]:
                            WkKDateD = int(WkKDateD) + 1
                        elif day_kbn == csDAYKBN_9:
                            WkKDateD = int(WkKDateD) + 1
                        else:
                            WkKDate = WkKDateY + "/" + WkKDateM + "/" + WkKDateD
                        if WkKDateD == "32" or tbcalen[i]["DAYKBN"][int(WkKDateD) - 1] == csDAYKBN_9:
                            WkKDate = WkKDateY + "/" + WkKDateM + "/01"
                            WkKDateY = CmfDateFmt(
                                (datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
                                "%Y")
                            WkKDateM = CmfDateFmt(
                                (datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
                                "%m")
                            WkKDateD = CmfDateFmt(
                                (datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
                                "%d")
                            WkKDate = ""
                    if not WkKDate == "":
                        break
                if WkFreeTime == "":
                    return DB_TBCALENDER_NOT_FIND
                else:
                    return WkFreeTime


    except IntegrityError as ie:
        _logger.error(ie)
        return DB_FATAL_ERR


def DbDataChange(DbStr):
    if not DbStr or DbStr == chr(0):
        return ""
    return DbStr


def pfncDataSessionGet(request, strSessionNM: str):
    try:
        return request.session.get(strSessionNM, None)
    except Exception as e:
        _logger.error(e)


def pfncDataSessionSet(request, strSessionNM: str, objData):
    try:
        request.session[strSessionNM] = objData
    except Exception as e:
        _logger.error(e)


def pfncDataSessionRelease(request, strSessionNM: str):
    try:
        del request.session[strSessionNM]
        request.session.modified = True
    except Exception as e:
        _logger.error(e)


def sqlStringConvert(strSQL):
    if not strSQL:
        strSQL = ""
    return f"'{strSQL}'"


def IsNumeric(obj):
    try:
        float(obj)
        return True
    except Exception:
        return False
