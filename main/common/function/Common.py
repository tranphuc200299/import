import logging
import psycopg2
from datetime import datetime
from time import sleep
from django.db import transaction
from dateutil.relativedelta import relativedelta
from main.common.function import SqlExecute
from main.common.function.Const import *
from main.common.function.DspMessage import *
from main.middleware.exception.exceptions import PostgresException

_logger = logging.getLogger(__name__)


def CmfDateFmt(rstrDate: str, input_format="%Y/%m/%d", output_format="%Y/%m/%d") -> str:
    # rintmode=2 ==> input_format="%Y-%m-%d", output_format="%Y/%m/%d"
    # rintmode=4 ==> input_format="%Y-%m-%d %H:%M:%S", output_format="%Y/%m/%d %H:%M:%S"
    try:
        return datetime.strptime(rstrDate, input_format).strftime(output_format)
    except Exception as e:
        _logger.error(e)
        return ""


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
        try:
            if '.' in strIn:
                int(strIn.split(".")[1])
            return float(strIn.replace(",", ""))
        except:
            return 0


def dbLong(strIn: str) -> int:
    if strIn == "":
        return 0
    else:
        return int(strIn)


def IsNumeric(obj):
    try:
        float(obj.replace(",", ""))
        return True
    except Exception:
        return False


def KijyunM3(objRsStani, strM3):
    if objRsStani.Rows and strM3 != "" and objRsStani.Rows[0]["syubtkbn"] != "2":
        if not objRsStani.Rows[0]["convert"]:
            dblConv = 0
        else:
            dblConv = float(objRsStani.Rows[0]["convert"])
        if IsNumeric(strM3.lstrip()):
            return dbsingle(strM3.lstrip()) * dblConv
    return 0


def KijyunWt(objRsStani, strWeight):
    if objRsStani.Rows and strWeight != "" and objRsStani.Rows[0]["syubtkbn"] != "1":
        if not objRsStani.Rows[0]["convert"]:
            dblConv = 0
        else:
            dblConv = float(objRsStani.Rows[0]["convert"])
        if IsNumeric(strWeight.lstrip()):
            return dbsingle(strWeight.lstrip()) * dblConv
    return 0


def CompRynTon(strM3: str) -> float:
    if IsNumeric(strM3.lstrip()):
        return dbsingle(strM3.lstrip()) / 1.133
    return 0


def MakeNaBlNo(objRsOpe, strCtBl):
    strDelChr = [""] * 3
    strDelLen = [0] * 3
    if strCtBl[:6] == "KKLUSH":
        return strCtBl
    if objRsOpe.Rows and strCtBl != "":
        if objRsOpe.Rows[0]["delchr1"] != chr(0):
            strDelChr[0] = objRsOpe.Rows[0]["delchr1"]
        if objRsOpe.Rows[0]["delchr2"] != chr(0):
            strDelChr[1] = objRsOpe.Rows[0]["delchr2"]
        if objRsOpe.Rows[0]["delchr3"] != chr(0):
            strDelChr[2] = objRsOpe.Rows[0]["delchr3"]
        if objRsOpe.Rows[0]["dellen1"] != chr(0):
            strDelLen[0] = objRsOpe.Rows[0]["dellen1"]
        if objRsOpe.Rows[0]["dellen2"] != chr(0):
            strDelLen[1] = objRsOpe.Rows[0]["dellen2"]
        if objRsOpe.Rows[0]["dellen3"] != chr(0):
            strDelLen[2] = objRsOpe.Rows[0]["dellen3"]
        if not objRsOpe.Rows[0]["scaccd"]:
            strScac = ""
        else:
            strScac = objRsOpe.Rows[0]["scaccd"]
        if not objRsOpe.Rows[0]["nscacflg"]:
            strNscacflg = ""
        else:
            strNscacflg = objRsOpe.Rows[0]["nscacflg"]

        if strDelLen[0] > 0:
            while strDelChr[0] in strCtBl:
                intBlLen = len(strCtBl)
                intPtr = strCtBl.index(strDelChr[0])
                strAns = strCtBl[:intPtr]
                strCtBl = strAns + strCtBl[(intPtr - 1 + strDelLen[0]) - intBlLen:]
        if strDelLen[1] > 0:
            while strDelChr[0] in strCtBl:
                intBlLen = len(strCtBl)
                intPtr = strCtBl.index(strDelChr[1])
                strAns = strCtBl[:intPtr]
                strCtBl = strAns + strCtBl[(intPtr - 1 + strDelLen[1]) - intBlLen:]
        if strDelLen[2] > 0:
            while strDelChr[0] in strCtBl:
                intBlLen = len(strCtBl)
                intPtr = strCtBl.index(strDelChr[2])
                strAns = strCtBl[:intPtr]
                strCtBl = strAns + strCtBl[(intPtr - 1 + strDelLen[2]) - intBlLen:]
        if strNscacflg == "y" or strNscacflg == "Y":
            return strScac + strCtBl
        return strCtBl
    else:
        return ""


def GetFreeTime(OpeCd, AreaCd, KDate, strSelTbl):
    try:
        WkErrTbl = "フリータイムテーブル"
        SqlStr = f"SELECT FKISANKBN, FDAYS, FCALC FROM TBFREETM{strSelTbl} WHERE "
        SqlStr += f"OPECD = {dbField(OpeCd)} AND "
        SqlStr += f"FREEKBN = {dbField(AreaCd)}"
        RsFreeTm = SqlExecute(SqlStr).all()
        if not RsFreeTm.Rows:
            return DB_TBFREETM_NOT_FIND
        WkFKISANKBN = RsFreeTm.Rows[0]["fkisankbn"]
        WkFDAYS = int(RsFreeTm.Rows[0]["fdays"]) - 1
        WkFCALC = RsFreeTm.Rows[0]["fcalc"]
        WkErrTbl = "カレンダーテーブル"
        SqlStr = f"SELECT YMDATE, DAYKBN FROM TBCALENDER{strSelTbl} WHERE "
        SqlStr += f"YMDATE >= {dbField(CmfDateFmt(KDate, output_format='%Y/%m'))}"
        SqlStr += " ORDER BY YMDATE"
        RsCalen = SqlExecute(SqlStr).all()
        if not RsCalen.Rows:
            return DB_TBCALENDER_NOT_FIND
        tbcalen = []
        tbcalen_cnt = len(RsCalen)
        for i in range(tbcalen_cnt):
            tbcalen.append({
                "YMDATE": RsCalen.Rows[i]["ymdate"],
                "YMDATEY": int(RsCalen.Rows[i]["ymdate"][0:4]),
                "YMDATEM": int(RsCalen.Rows[i]["ymdate"][5:7]),
                "DAYKBN": RsCalen.Rows[i]["daykbn"]
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
            if WkFCALC == csFCALC_3:
                WkKDate = WkKDateY + "/" + WkKDateM + "/" + WkKDateD
            else:
                WkKDate = ""
                for i in range(tbcalen_cnt):
                    if WkKDate != "":
                        break
                    if tbcalen[i]["ymdate"] == WkKDateY + "/" + WkKDateM:
                        day_kbn = tbcalen[i]["daykbn"][int(WkKDateD) - 1]
                        if day_kbn == csDAYKBN_2:
                            if WkFCALC == csFCALC_1:
                                WkKDate = WkKDateY + "/" + WkKDateM + "/" + WkKDateD
                                continue
                            else:
                                WkKDateD = int(WkKDateD) + 1
                        elif day_kbn in [csDAYKBN_3, csDAYKBN_4]:
                            WkKDateD = int(WkKDateD) + 1
                        elif day_kbn == csDAYKBN_9:
                            WkKDateD = int(WkKDateD) + 1
                        else:
                            WkKDate = WkKDateY + "/" + WkKDateM + "/" + WkKDateD
                            continue
                        if WkKDateD == "32" or tbcalen[i]["daykbn"][int(WkKDateD) - 2] == csDAYKBN_9:
                            WkKDate = WkKDateY + "/" + WkKDateM + "/01"
                            WkKDateY = CmfDateFmt(
                                (datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                                "%Y")
                            WkKDateM = CmfDateFmt(
                                (datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                                "%m")
                            WkKDateD = CmfDateFmt(
                                (datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                                "%d")
                            WkKDate = ""
                            continue
                    else:
                        WkKDate = ""
                if WkKDate == "":
                    return DB_TBCALENDER_NOT_FIND
        if WkFCALC == csFCALC_3 or WkFDAYS == 0:
            WkFreeTime = CmfDateFmt(
                (datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=WkFDAYS)).strftime("%Y/%m/%d"),
                "%Y/%m/%d")
            return WkFreeTime
        WkKDateY = CmfDateFmt((datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
                              "%Y")
        WkKDateM = CmfDateFmt((datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
                              "%m")
        WkKDateD = CmfDateFmt((datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
                              "%d")
        WkFreeTime = ""
        WkFCnt = 0
        for i in range(tbcalen_cnt):
            if WkFreeTime != "":
                break
            if tbcalen[i]["ymdate"] == WkKDateY + "/" + WkKDateM:
                if tbcalen[i]["daykbn"][int(WkKDateD) - 1] == csDAYKBN_9:
                    WkFreeTime = WkKDateY + "/" + WkKDateM + "/01"
                    WkKDateY = CmfDateFmt(
                        (datetime.strptime(WkFreeTime, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                        "%Y")
                    WkKDateM = CmfDateFmt(
                        (datetime.strptime(WkFreeTime, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                        "%m")
                    WkKDateD = CmfDateFmt(
                        (datetime.strptime(WkFreeTime, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                        "%d")
                    WkFreeTime = ""
                    continue
                if not tbcalen[i]["ymdate"] == WkKDateY + "/" + WkKDateM:
                    continue
                if tbcalen[i]["daykbn"][int(WkKDateD) - 1] == csDAYKBN_1:
                    WkFCnt = WkFCnt + 1
                if WkFCALC == csFCALC_1 and tbcalen[i]["daykbn"][int(WkKDateD) - 1] == csDAYKBN_2:
                    WkFCnt = WkFCnt + 1
                if WkFCnt == WkFDAYS:
                    WkFreeTime = WkKDateY + "/" + WkKDateM + "/" + WkKDateD
                    continue
                WkFreeTime = WkKDateY + "/" + WkKDateM + "/" + WkKDateD
                WkKDateY = CmfDateFmt(
                    (datetime.strptime(WkFreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%Y")
                WkKDateM = CmfDateFmt(
                    (datetime.strptime(WkFreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%m")
                WkKDateD = CmfDateFmt(
                    (datetime.strptime(WkFreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%d")
                WkFreeTime = ""

        if WkFreeTime == "":
            return DB_TBCALENDER_NOT_FIND
        else:
            return WkFreeTime

    except Exception as e:
        _logger.error(e)
        return DB_FATAL_ERR


def VanDigit_Check(strVanNo):
    vntVanChr = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                 "U", "V",
                 "W", "X", "Y", "Z", "*"]
    vntVanNum = ["10", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "23", "24", "25", "26", "27", "28",
                 "29",
                 "30", "31", "32", "34", "35", "36", "37", "38", "*"]
    if strVanNo[:3] == TRACK_VANNO:
        return NOMAL_OK
    if len(strVanNo) != 11:
        return FATAL_ERR
    for i in range(4):
        if strVanNo[i] not in vntVanChr[:-1]:
            return FATAL_ERR
    for i in range(4, 11):
        if not IsNumeric(strVanNo[i]):
            return FATAL_ERR
    intKeisuu = 1
    lngGoukei = 0
    for i in range(4):
        lngGoukei = lngGoukei + int(vntVanNum[vntVanChr.index(strVanNo[i])]) * intKeisuu
        intKeisuu = intKeisuu * 2
    for i in range(4, 10):
        lngGoukei = lngGoukei + int(strVanNo[i]) * intKeisuu
        intKeisuu = intKeisuu * 2
    lngSyou = int(lngGoukei / 11)
    lngAmari = lngGoukei - lngSyou
    lngKotae = lngAmari * 11
    if strVanNo[-1] == str(lngKotae)[-1]:
        return NOMAL_OK
    else:
        return FATAL_ERR


def HomePortGet(strSelTbl, strSelHozCd):
    sql = ""
    try:
        sql = "SELECT HPORTCD "
        sql += f"FROM TBCFSSYS{strSelTbl} "
        sql += f"WHERE HOZEICD = {dbField(strSelHozCd)}"
        RsTbCfsSys = SqlExecute(sql).all()
        if not RsTbCfsSys.Rows or RsTbCfsSys.Rows[0]["hportcd"] == chr(0):
            return ""
        else:
            return RsTbCfsSys.Rows[0]["hportcd"]
    except psycopg2.OperationalError as e:
        raise PostgresException(Error=e, DbTbl="TBCFSSYS" + strSelTbl, SqlStr=sql)


def GetDemurg(GDemurg, strSelTbl):
    try:
        WkErrTbl = "カレンダーテーブル"
        SqlStr = f"SELECT YMDATE, DAYKBN FROM TBCALENDER{strSelTbl} WHERE "
        SqlStr += f"YMDATE >= {dbField(CmfDateFmt(GDemurg['FreeTime'], '%Y/%m'))}"
        SqlStr += " ORDER BY YMDATE"
        RsCalen = SqlExecute(SqlStr).all()
        if not RsCalen.Rows:
            return DB_TBCALENDER_NOT_FIND
        tbcalen = []
        tbcalen_cnt = len(RsCalen)
        for i in range(tbcalen_cnt):
            tbcalen[i]["ymdate"] = RsCalen.Rows[i]["ymdate"]
            tbcalen[i]["ymdatey"] = int(RsCalen.Rows[i]["ymdate"][:4])
            tbcalen[i]["ymdatem"] = int(RsCalen.Rows[i]["ymdate"][5:7])
            tbcalen[i]["daykbn"] = RsCalen.Rows[i]["daykbn"]
        WkErrTbl = "デマレージテーブル"
        SqlStr = "SELECT "
        SqlStr += "A.OPECD AS OPECD1, "
        SqlStr += "A.MINTON AS MINTON, "
        SqlStr += "B.OPECD AS OPECD2, "
        SqlStr += "B.RANK1 AS RANK1, "
        SqlStr += "B.RANK2 AS RANK2, "
        SqlStr += "B.RANK3 AS RANK3, "
        SqlStr += "B.RANK4 AS RANK4, "
        SqlStr += "B.RANK5 AS RANK5, "
        SqlStr += "B.TANKA1 AS TANKA1, "
        SqlStr += "B.TANKA2 AS TANKA2, "
        SqlStr += "B.TANKA3 AS TANKA3, "
        SqlStr += "B.TANKA4 AS TANKA4, "
        SqlStr += "B.TANKA5 AS TANKA5, "
        SqlStr += "B.STANKAKBN AS STANKAKBN, "
        SqlStr += "B.TANKAC AS TANKAC, "
        SqlStr += "B.DCALC AS DCALC "
        SqlStr += "FROM "
        SqlStr += f"TBOPE{strSelTbl} A, "
        SqlStr += f" LEFT OUTER JOIN TBDEMURG{strSelTbl} B ON B.OPECD = A.OPECD"
        SqlStr += f"WHERE A.OPECD = {dbField(GDemurg['OpeCd'])} "
        RsDemu = SqlExecute(SqlStr).all()
        if not RsDemu.Rows:
            return DB_TBOPE_NOT_FIND
        if not RsDemu.Rows[0]["opecd2"]:
            return DB_TBDEMURG_NOT_FIND

        WkMinTon = int(RsDemu.Rows[0]["minton"])
        GDemurg["MinTon"] = int(RsDemu.Rows[0]["minton"])
        tbdemurg = []
        for i in range(1, 6):
            tbdemurg.append({
                "RANK": int(RsDemu.Rows[0]["rank" + str(i)]),
                "TANKA": round(RsDemu.Rows[0]["tanka" + str(i)])
            })
        if RsDemu.Rows[0]["stankakbn"] == csSTANKAKBN_2:
            WkDemurg = GDemurg["KMeasur"]
        elif RsDemu.Rows[0]["stankakbn"] == csSTANKAKBN_3:
            WkDemurg = GDemurg["KWeight"] / 1000
        else:
            WkDemurg = GDemurg["RynTon"]

        if GDemurg["MtonTKbn"] == csMTONTKBN_2:
            WkDemurg = WkMinTon
        elif GDemurg["MtonTKbn"] == csMTONTKBN_3:
            if WkMinTon > WkDemurg:
                WkDemurg = WkMinTon
        GDemurg["STANKAKBN"] = RsDemu.Rows[0]["stankakbn"]
        WkTankaC = dbLong(RsDemu.Rows[0]["tankac"])
        WkDCalc = RsDemu.Rows[0]["dcalc"]
        WkDateY = CmfDateFmt(
            (datetime.strptime(GDemurg["FreeTime"], "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%Y")
        WkDateM = CmfDateFmt(
            (datetime.strptime(GDemurg["FreeTime"], "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%m")
        WkDateD = CmfDateFmt(
            (datetime.strptime(GDemurg["FreeTime"], "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%d")
        WkDate = WkDateY + "/" + WkDateM + "/" + WkDateD
        WkNisu = 0
        WkEndFlg = 0
        for i in range(tbcalen_cnt):
            if WkEndFlg == 9:
                break
            day_kbn = tbcalen[i]["daykbn"][int(WkDateD) - 1]
            if tbcalen[i]["ymdate"] + "/" + f"{WkDateD:02}" > GDemurg["OutDate"]:
                WkEndFlg = 9
                continue
            if day_kbn == csDAYKBN_2:
                if WkDCalc in [csDCALC_1, csDCALC_3]:
                    WkNisu = WkNisu + 1
            elif day_kbn in [csDAYKBN_3, csDAYKBN_4]:
                if WkDCalc == csDCALC_3:
                    WkNisu = WkNisu + 1
            elif day_kbn == csDAYKBN_9:
                pass
            else:
                WkNisu = WkNisu + 1
            WkDateD = f"{int(WkDateD) + 1 :02}"
            if WkDateD == "32" or tbcalen[i]["daykbn"][int(WkDateD) - 2] == csDAYKBN_9:
                WkDate = WkDateY + "/" + WkDateM + "/01"
                WkDateY = CmfDateFmt(
                    (datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                    "%Y")
                WkDateM = CmfDateFmt(
                    (datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                    "%m")
                WkDateD = CmfDateFmt(
                    (datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                    "%d")
                WkDate = ""
        if WkEndFlg == 0:
            return DB_TBCALENDER_NOT_FIND
        if WkNisu == 0:
            GDemurg["demurg"] = 0
            return DB_NOMAL_OK
        if WkTankaC == 0:
            GDemurg["DemuCKbn"] = csDEMUCKBN_A
            for i in range(len(tbdemurg)):
                if WkNisu <= tbdemurg[i]["rank"]:
                    GDemurg["DemuTanka"] = tbdemurg[i]["tanka"]
                    GDemurg["demurg"] = tbdemurg[i]["tanka"] * WkNisu * WkDemurg
                    GDemurg["DemurgN"] = WkNisu
                    break
        else:
            GDemurg["DemuCKbn"] = csDEMUCKBN_C
            for i in range(len(tbdemurg)):
                if WkNisu <= tbdemurg[i]["rank"]:
                    GDemurg["CDemuTanka1"] = tbdemurg[i]["tanka"]
                    GDemurg["CDemuTanka2"] = 0
                    GDemurg["demurg"] = tbdemurg[i]["tanka"] * WkNisu * WkDemurg
                    GDemurg["CDemurgN1"] = WkNisu
                    GDemurg["CDemurgN2"] = 0
                    break
                else:
                    if i != 4:
                        if tbdemurg[i + 1]["rank"] == 0:
                            GDemurg["CDemuTanka1"] = tbdemurg[i]["tanka"]
                            GDemurg["CDemuTanka2"] = WkTankaC * (WkNisu - tbdemurg[i]["rank"])
                            GDemurg["demurg"] = (tbdemurg[i]["tanka"] * tbdemurg[i]["rank"] * WkDemurg) + (
                                    WkTankaC * (WkNisu - tbdemurg[i]["rank"]) * WkDemurg)
                            GDemurg["CDemurgN1"] = tbdemurg[i]["rank"]
                            GDemurg["CDemurgN2"] = WkNisu - tbdemurg[i]["rank"]
                            break
            if GDemurg["demurg"] == 0:
                GDemurg["CDemuTanka1"] = tbdemurg[4]["tanka"]
                GDemurg["CDemuTanka2"] = WkTankaC * (WkNisu - tbdemurg[4]["rank"])
                GDemurg["demurg"] = (tbdemurg[4]["tanka"] * tbdemurg[4]["rank"] * WkDemurg) + (
                        WkTankaC * (WkNisu - tbdemurg[4]["rank"]) * WkDemurg)
                GDemurg["CDemurgN1"] = tbdemurg[4]["rank"]
                GDemurg["CDemurgN2"] = WkNisu - tbdemurg[4]["rank"]
        return DB_NOMAL_OK
    except Exception as e:
        _logger.error(e)
        return DB_FATAL_ERR


def GetDemurg2(GDemurg, strSelTbl):
    try:
        WkDemurg = 0
        WkErrTbl = "カレンダーテーブル"
        SqlStr = f"SELECT YMDATE, DAYKBN FROM TBCALENDER{strSelTbl} WHERE "
        SqlStr += f"YMDATE >= {dbField(CmfDateFmt(GDemurg['FreeTime'], '%Y/%m'))}"
        SqlStr += " ORDER BY YMDATE"
        RsCalen = SqlExecute(SqlStr).all()
        if not RsCalen.Rows:
            return DB_TBCALENDER_NOT_FIND
        tbcalen = []
        tbcalen_cnt = len(RsCalen)
        for i in range(tbcalen_cnt):
            tbcalen[i]["ymdate"] = RsCalen.Rows[i]["ymdate"]
            tbcalen[i]["ymdatey"] = int(RsCalen.Rows[i]["ymdate"][:4])
            tbcalen[i]["ymdatem"] = int(RsCalen.Rows[i]["ymdate"][5:7])
            tbcalen[i]["daykbn"] = RsCalen.Rows[i]["daykbn"]
        WkErrTbl = "デマレージテーブル"
        SqlStr = "SELECT "
        SqlStr += "B.OPECD AS OPECD, "
        SqlStr += "B.RANK1 AS RANK1, "
        SqlStr += "B.RANK2 AS RANK2, "
        SqlStr += "B.RANK3 AS RANK3, "
        SqlStr += "B.RANK4 AS RANK4, "
        SqlStr += "B.RANK5 AS RANK5, "
        SqlStr += "B.TANKA1 AS TANKA1, "
        SqlStr += "B.TANKA2 AS TANKA2, "
        SqlStr += "B.TANKA3 AS TANKA3, "
        SqlStr += "B.TANKA4 AS TANKA4, "
        SqlStr += "B.TANKA5 AS TANKA5, "
        SqlStr += "B.TANKAC AS TANKAC, "
        SqlStr += "B.DCALC AS DCALC "
        SqlStr += "FROM "
        SqlStr += f"TBDEMURG{strSelTbl} B "
        SqlStr += "WHERE "
        SqlStr += f"B.OPECD = {dbField(GDemurg['OpeCd'])}"
        RsDemu = SqlExecute(SqlStr).all()
        if not RsDemu.Rows:
            return DB_TBDEMURG_NOT_FIND
        tbdemurg = []
        WkRankMax = 0
        for i in range(1, 6):
            tbdemurg.append({
                "RANK": int(RsDemu.Rows[0]["rank" + str(i)]),
                "TANKA": round(RsDemu.Rows[0]["tanka" + str(i)])
            })
            if WkRankMax < int(RsDemu.Rows[0]["rank" + str(i)]):
                WkRankMax = int(RsDemu.Rows[0]["rank" + str(i)])
        if GDemurg["MtonTKbn"] == csMTONTKBN_1:
            WkDemurg = GDemurg["RynTon"]
        elif GDemurg["MtonTKbn"] == csMTONTKBN_2:
            WkDemurg = GDemurg["MinTon"]
        elif GDemurg["MtonTKbn"] == csMTONTKBN_3:
            if GDemurg["RynTon"] > GDemurg["MinTon"]:
                WkDemurg = GDemurg["RynTon"]
            else:
                WkDemurg = GDemurg["MinTon"]

        WkTankaC = dbLong(RsDemu.Rows[0]["tankac"])
        WkDCalc = RsDemu.Rows[0]["dcalc"]
        WkDateY = CmfDateFmt(
            (datetime.strptime(GDemurg["FreeTime"], "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
            "%Y")
        WkDateM = CmfDateFmt(
            (datetime.strptime(GDemurg["FreeTime"], "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
            "%m")
        WkDateD = CmfDateFmt(
            (datetime.strptime(GDemurg["FreeTime"], "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
            "%d")
        WkDate = WkDateY + "/" + WkDateM + "/" + WkDateD
        WkNisu = 0
        WkEndFlg = 0
        for i in range(tbcalen_cnt):
            if WkEndFlg == 9:
                break
            if tbcalen[i]["ymdate"] >= WkDateY + "/" + WkDateM:
                WkEndFlg = 9
                continue
            day_kbn = tbcalen[i]["daykbn"][int(WkDateD) - 1]
            if day_kbn == csDAYKBN_2:
                if WkDCalc == csDCALC_1 or WkDCalc == csDCALC_3:
                    WkNisu = WkNisu + 1
            elif day_kbn in [csDAYKBN_3, csDAYKBN_4]:
                if WkDCalc == csDCALC_3:
                    WkNisu = WkNisu + 1
            elif day_kbn == csDAYKBN_9:
                pass
            else:
                WkNisu = WkNisu + 1
            WkDateD = f"{int(WkDateD) + 1 :02}"
            if WkDateD == "32" or tbcalen[i]["daykbn"][int(WkDateD) - 2] == csDAYKBN_9:
                WkDate = WkDateY + "/" + WkDateM + "/01"
                WkDateY = CmfDateFmt(
                    (datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                    "%Y")
                WkDateM = CmfDateFmt(
                    (datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                    "%m")
                WkDateD = CmfDateFmt(
                    (datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                    "%d")
                WkDate = ""
        if WkEndFlg == 0:
            return DB_TBCALENDER_NOT_FIND
        if WkNisu == 0:
            GDemurg["demurg"] = 0
            GDemurg["demurgN"] = 0
            return DB_NOMAL_OK
        if WkTankaC == 0:
            GDemurg["DemuCKbn"] = csDEMUCKBN_A
            for i in range(len(tbdemurg)):
                if WkNisu <= tbdemurg[i]["rank"]:
                    GDemurg["DemuTanka"] = tbdemurg[i]["tanka"]
                    GDemurg["demurg"] = f"{tbdemurg[i]['tanka'] * WkNisu * WkDemurg :01}"
                    GDemurg["demurgN"] = WkNisu
                    break
                else:
                    if WkRankMax == tbdemurg[i]["rank"]:
                        if WkNisu >= tbdemurg[i]["rank"]:
                            GDemurg["DemuTanka"] = tbdemurg[i]["tanka"]
                            GDemurg["demurg"] = f"{tbdemurg[i]['tanka'] * WkNisu * WkDemurg :01}"
                            GDemurg["demurgN"] = WkNisu
                            break
        else:
            GDemurg["DemuCKbn"] = csDEMUCKBN_C
            for i in range(len(tbdemurg)):
                if WkNisu <= tbdemurg[i]["rank"]:
                    GDemurg["CDemuTanka1"] = tbdemurg[i]["tanka"]
                    GDemurg["CDemuTanka2"] = 0
                    GDemurg["demurg"] = f"{tbdemurg[i]['tanka'] * WkNisu * WkDemurg :01}"
                    GDemurg["CDemurgN1"] = WkNisu
                    GDemurg["CDemurgN2"] = 0
                    break
                else:
                    if i != 4:
                        if tbdemurg[i + 1]["rank"] == 0:
                            GDemurg["CDemuTanka1"] = tbdemurg[i]["tanka"]
                            GDemurg["CDemuTanka2"] = WkTankaC * (WkNisu - tbdemurg[i]["rank"])
                            GDemurg[
                                "demurg"] = f"{(tbdemurg[i]['tanka'] * tbdemurg[i]['rank'] * WkDemurg) + (WkTankaC * (WkNisu - tbdemurg[i]['rank']) * WkDemurg) :01}"
                            GDemurg["CDemurgN1"] = tbdemurg[i]["rank"]
                            GDemurg["CDemurgN2"] = WkNisu - tbdemurg[i]["rank"]
                            break

            if GDemurg["demurg"] == 0:
                GDemurg["CDemuTanka1"] = tbdemurg[4]["tanka"]
                GDemurg["CDemuTanka2"] = WkTankaC * (WkNisu - tbdemurg[4]["rank"])
                GDemurg[
                    "demurg"] = f"{(tbdemurg[4]['tanka'] * tbdemurg[4]['rank'] * WkDemurg) + (WkTankaC * (WkNisu - tbdemurg[4]['rank']) * WkDemurg) :01}"
                GDemurg["CDemurgN1"] = tbdemurg[4]["rank"]
                GDemurg["CDemurgN2"] = WkNisu - tbdemurg[4]["rank"]
        return DB_NOMAL_OK
    except Exception as e:
        _logger.error(e)
        return DB_FATAL_ERR


def GetSeikyuNo(ProgramId, SystemData, iniUpdCd, iniWsNo):
    try:
        NowDate = ""
        GetFlg = 0
        for i in range(11):
            status, NowDate = TbCfsSysSELECT(SystemData, csLOCK_ON, iniUpdCd)
            if status == DB_NOMAL_OK:
                GetFlg = 1
                break
            elif status == DB_LOCK:
                GetFlg = 0
            sleep(1)

        if GetFlg == 0:
            return DB_LOCK
        SeikyuHead = SystemData["SEIKYUHNO"][:6]
        if SeikyuHead == NowDate[:6]:
            SeikyuSeq = round(float(SystemData["SEIKYUHNO"][6:11])) + 1
        else:
            SeikyuHead = NowDate[:6]
            SeikyuSeq = 1
        SystemData["SEIKYUHNO"] = SeikyuHead + f"{SeikyuSeq:04}"
        SeikyuNo = SystemData["SEIKYUHNO"]
        with transaction.atomic():
            SqlStr = "UPDATE TBCFSSYS{strSelTbl} SET "
            SqlStr += f"SEIKYUHNO = {dbField(SystemData['SEIKYUHNO'])}, "
            SqlStr += "UDATE = CURRENT_TIMESTAMP, "
            SqlStr += f"UPROGID = {dbField(ProgramId)}, "
            SqlStr += f"UWSID = {dbField(iniWsNo)}"
            SqlStr += f" WHERE HOZEICD = {dbField(SystemData['HOZEICD'])}"
            SqlExecute(SqlStr).execute()
        return DB_NOMAL_OK, SeikyuNo
    except psycopg2.OperationalError as e:
        raise PostgresException(Error=e, DbTbl="CFSシステムテーブル", SqlStr=SqlStr)


def TbCfsSysSELECT(SystemData, LockKbn, iniUpdCd):
    SqlStr = ""
    try:
        SqlStr += "SELECT "
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
        SqlStr += "SEIKYUHNO, "
        SqlStr += "TO_CHAR(CURRENT_TIMESTAMP,'YYYYMMDD') AS NOWDATE "
        SqlStr += f"FROM TBCFSSYS{iniUpdCd}"
        SqlStr += " WHERE "
        SqlStr += f"HOZEICD = {dbField(SystemData['HOZEICD'])}"
        if LockKbn == csLOCK_ON:
            SqlStr += " FOR UPDATE NOWAIT"
        RsSys = SqlExecute(SqlStr).all()
        if not RsSys.Rows:
            return DB_NOT_FIND
        SystemData["COMPANYNM"] = DbDataChange(RsSys.Rows[0]["companynm"])
        SystemData["BRANCHNM"] = DbDataChange(RsSys.Rows[0]["branchnm"])
        SystemData["JIMUSYCD"] = DbDataChange(RsSys.Rows[0]["jimusycd"])
        SystemData["JIMUSYNM"] = DbDataChange(RsSys.Rows[0]["jimusynm"])
        SystemData["JIMUSYADR"] = DbDataChange(RsSys.Rows[0]["jimusyadr"])
        SystemData["JIMUSYTEL"] = DbDataChange(RsSys.Rows[0]["jimusytel"])
        SystemData["JIMUSYFAX"] = DbDataChange(RsSys.Rows[0]["jimusyfax"])
        SystemData["KEIJIMSG"] = DbDataChange(RsSys.Rows[0]["keijimsg"])
        SystemData["HPORTCD"] = DbDataChange(RsSys.Rows[0]["hportcd"])
        SystemData["HOZEINM"] = DbDataChange(RsSys.Rows[0]["hozeinm"])
        SystemData["GWSKBN"] = DbDataChange(RsSys.Rows[0]["gwskbn"])
        SystemData["GW1IP"] = DbDataChange(RsSys.Rows[0]["gw1ip"])
        SystemData["GW1USERID"] = DbDataChange(RsSys.Rows[0]["gw1userid"])
        SystemData["GW1PASSWD"] = DbDataChange(RsSys.Rows[0]["gw1passwd"])
        SystemData["GW1NAME"] = DbDataChange(RsSys.Rows[0]["gw1name"])
        SystemData["GW1SDIR"] = DbDataChange(RsSys.Rows[0]["gw1sdir"])
        SystemData["GW2IP"] = DbDataChange(RsSys.Rows[0]["gw2ip"])
        SystemData["GW2USERID"] = DbDataChange(RsSys.Rows[0]["gw2userid"])
        SystemData["GW2PASSWD"] = DbDataChange(RsSys.Rows[0]["gw2passwd"])
        SystemData["GW2NAME"] = DbDataChange(RsSys.Rows[0]["gw2name"])
        SystemData["GW2SDIR"] = DbDataChange(RsSys.Rows[0]["gw2sdir"])
        SystemData["USERCD"] = DbDataChange(RsSys.Rows[0]["usercd"])
        SystemData["IDCD1"] = DbDataChange(RsSys.Rows[0]["idcd1"])
        SystemData["USERPSWD1"] = DbDataChange(RsSys.Rows[0]["userpswd1"])
        SystemData["IDCD2"] = DbDataChange(RsSys.Rows[0]["idcd2"])
        SystemData["USERPSWD2"] = DbDataChange(RsSys.Rows[0]["userpswd2"])
        SystemData["IOJNOHEAD"] = DbDataChange(RsSys.Rows[0]["iojnohead"])
        SystemData["IOJNOMIN"] = DbDataChange(RsSys.Rows[0]["iojnomin"])
        SystemData["IOJNOMAX"] = DbDataChange(RsSys.Rows[0]["iojnomax"])
        SystemData["IOJNONOW"] = DbDataChange(RsSys.Rows[0]["iojnonow"])
        SystemData["UNQFILENM"] = DbDataChange(RsSys.Rows[0]["unqfilenm"])
        SystemData["TAXNEW"] = DbDataChange(RsSys.Rows[0]["taxnew"])
        SystemData["TAXOLD"] = DbDataChange(RsSys.Rows[0]["taxold"])
        SystemData["TAXCHG"] = DbDataChange(RsSys.Rows[0]["taxchg"])
        SystemData["GENGONEW"] = DbDataChange(RsSys.Rows[0]["gengonew"])
        SystemData["GENGOOLD"] = DbDataChange(RsSys.Rows[0]["gengoold"])
        SystemData["GENGOCHG"] = DbDataChange(RsSys.Rows[0]["gengochg"])
        SystemData["SEIKYUHNO"] = DbDataChange(RsSys.Rows[0]["seikyuhno"])
        NowDate = DbDataChange(RsSys.Rows[0]["nowdate"])
        return DB_NOMAL_OK, NowDate
    except psycopg2.OperationalError as e:
        if e.pgcode == "55P03":
            return DB_LOCK, None
        else:
            raise PostgresException(Error=e, DbTbl="CFSシステムテーブル", SqlStr=SqlStr)


def DbDataChange(DbStr):
    if not DbStr or DbStr == chr(0):
        return ""
    return DbStr


def GetRevenue(OpeCd, KGWeight, M3Measur, RynDataCnt, RynData, strSelTbl):
    SqlStr = ""
    RynTon = None
    MinTon = None
    try:
        WkSTankaKbn = ""
        if RynDataCnt == 0:
            RynData = []
        else:
            for i in range(len(RynData)):
                if RynData[i]["opecd"] == OpeCd:
                    WkSTankaKbn = RynData[i]["stankakbn"]
                    MinTon = RynData[i]["minton"]
        if WkSTankaKbn == "":
            SqlStr = "SELECT "
            SqlStr += "A.MINTON AS MINTON, "
            SqlStr += "B.STANKAKBN "
            SqlStr += "FROM "
            SqlStr += f"TBOPE{strSelTbl} A, "
            SqlStr += f"TBDEMURG{strSelTbl} B "
            SqlStr += "WHERE "
            SqlStr += f"A.OPECD = {dbField(OpeCd)}"
            SqlStr += " AND B.OPECD = A.OPECD"
            RsDb = SqlExecute(SqlStr).all()
            if not RsDb.Rows:
                return DB_NOT_FIND, None, None
            RynDataCnt += 1
            RynData[- 1]["OpeCd"] = OpeCd
            RynData[- 1]["STANKAKBN"] = DbDataChange(RsDb.Rows[0]["stankakbn"])
            RynData[- 1]["MinTon"] = int(DbDataChange(RsDb.Rows[0]["minton"]))
            WkSTankaKbn = DbDataChange(RsDb.Rows[0]["stankakbn"])
            MinTon = int(DbDataChange(RsDb.Rows[0]["minton"]))

        if WkSTankaKbn == csSTANKAKBN_1:
            if (KGWeight / 1000) > M3Measur:
                RynTon = KGWeight / 1000
            else:
                RynTon = M3Measur
        elif WkSTankaKbn == csSTANKAKBN_2:
            RynTon = M3Measur
        elif WkSTankaKbn == csSTANKAKBN_3:
            RynTon = KGWeight / 1000
        elif WkSTankaKbn == csSTANKAKBN_4:
            if (KGWeight / 1000) > CompRynTon(f"{M3Measur :,.3f}"):
                RynTon = KGWeight / 1000
            else:
                RynTon = CompRynTon(f"{M3Measur :,.3f}")
        elif WkSTankaKbn == csSTANKAKBN_5:
            RynTon = CompRynTon(f"{M3Measur :,.3f}")
        return DB_NOMAL_OK, RynTon, MinTon
    except psycopg2.OperationalError as e:
        raise PostgresException(Error=e, DbTbl="", SqlStr=SqlStr)


def sqlStringConvert(strSQL):
    if not strSQL:
        strSQL = ""
    return f"'{strSQL}'"


def GetDemurgKDate(OpeCd, FreeTime, strSelTbl, WkDCalc):
    demurgKDate = ""
    try:
        WkEndFlg = None
        WkDateY = CmfDateFmt(
            (datetime.strptime(FreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%Y")
        WkDateM = CmfDateFmt(
            (datetime.strptime(FreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%m")
        WkDateD = CmfDateFmt(
            (datetime.strptime(FreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%d")
        WkDate = WkDateY + "/" + WkDateM + "/" + WkDateD
        WkErrTbl = "カレンダーテーブル"
        SqlStr = "SELECT YMDATE, DAYKBN FROM TBCALENDER{strSelTbl} WHERE "
        SqlStr += f"YMDATE >= {dbField(WkDateY + '/' + WkDateM)}"
        SqlStr += " ORDER BY YMDATE"
        RsCalen = SqlExecute(SqlStr).all()
        if not RsCalen.Rows:
            return DB_TBDEMURG_NOT_FIND

        tbcalen = []
        tbcalen_cnt = len(RsCalen)
        for i in range(tbcalen_cnt):
            tbcalen[i]["ymdate"] = RsCalen.Rows[i]["ymdate"]
            tbcalen[i]["ymdatey"] = int(RsCalen.Rows[i]["ymdate"][:4])
            tbcalen[i]["ymdatem"] = int(RsCalen.Rows[i]["ymdate"][5:7])
            tbcalen[i]["daykbn"] = RsCalen.Rows[i]["daykbn"]
        WkErrTbl = "デマレージテーブル"
        SqlStr = "SELECT "
        SqlStr += "DCALC "
        SqlStr += "FROM "
        SqlStr += f"TBDEMURG{strSelTbl}"
        SqlStr += " WHERE "
        SqlStr += f"OPECD = {dbField(OpeCd)}"
        RsDemu = SqlExecute(SqlStr).all()
        if not RsDemu.Rows:
            return DB_TBDEMURG_NOT_FIND
        WkDCalc = RsDemu.Rows[0]["dcalc"]
        for i in range(tbcalen_cnt):
            if WkEndFlg == 9:
                break
            day_kbn = tbcalen[i]["daykbn"][int(WkDateD) - 1]
            if day_kbn == csDAYKBN_2:
                if WkDCalc in [csDCALC_1, csDCALC_3]:
                    demurgKDate = tbcalen[i]["ymdate"] + "/" + WkDateD
                    WkEndFlg = 9
                    continue
            elif day_kbn in [csDAYKBN_3, csDAYKBN_4]:
                if WkDCalc == csDCALC_3:
                    demurgKDate = tbcalen[i]["ymdate"] + "/" + WkDateD
                    WkEndFlg = 9
                    continue
            elif day_kbn == csDAYKBN_9:
                pass
            else:
                demurgKDate = tbcalen[i]["ymdate"] + "/" + WkDateD
                WkEndFlg = 9
            WkDateD = f"{int(WkDateD) + 1 :02}"
            if WkDateD == "32" or tbcalen[i]["daykbn"][int(WkDateD) - 2] == csDAYKBN_9:
                WkDate = WkDateY + "/" + WkDateM + "/01"
                WkDateY = CmfDateFmt(
                    (datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                    "%Y")
                WkDateM = CmfDateFmt(
                    (datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                    "%m")
                WkDateD = CmfDateFmt(
                    (datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                    "%d")
                WkDate = ""
        return demurgKDate
    except Exception as e:
        _logger.error(e)
        return DB_FATAL_ERR


def Cm_TbOpeChk(strProcTbl, strOpeCd):
    sql = ""
    try:
        sql = "SELECT OPENM "
        sql += f"FROM TBOPE{strProcTbl} "
        sql += f"WHERE OPECD = {dbField(strOpeCd)}"
        return SqlExecute(sql)
    except psycopg2.OperationalError as e:
        raise PostgresException(Error=e, DbTbl="TBOPE" + strProcTbl, SqlStr=sql)


def Cm_TbVesselChk(strProcTbl, strVesselCd):
    sql = ""
    try:
        sql = "SELECT * "
        sql += f"FROM TBVESSEL{strProcTbl} "
        sql += f"WHERE VESSELCD = {dbField(strVesselCd)}"
        return SqlExecute(sql)
    except psycopg2.OperationalError as e:
        raise PostgresException(Error=e, DbTbl="TBVESSEL" + strProcTbl, SqlStr=sql)


def Cm_TbDemurgChk(strProcTbl, strOpeCd):
    sql = ""
    try:
        sql = "SELECT STANKAKBN "
        sql += f"FROM TBDEMURG{strProcTbl} "
        sql += f"WHERE OPECD = {dbField(strOpeCd)}"
        return SqlExecute(sql)
    except psycopg2.OperationalError as e:
        raise PostgresException(Error=e, DbTbl="TBDEMURG" + strProcTbl, SqlStr=sql)


def Cm_TbForwardChk(strProcTbl, strFwdCd):
    sql = ""
    try:
        sql = "SELECT FWDNM,FWDTANNM,FWDTEL,FWDFAX "
        sql += f"FROM TBFORWARD{strProcTbl} "
        sql += f"WHERE FWDCD = {dbField(strFwdCd)}"
        return SqlExecute(sql)
    except psycopg2.OperationalError as e:
        raise PostgresException(Error=e, DbTbl="TBFORWARD" + strProcTbl, SqlStr=sql)


def Cm_TbZWorkChk(strProcTbl, strZWorkCd):
    sql = ""
    try:
        sql = "SELECT ZWORKNM "
        sql += f"FROM TBZWORK{strProcTbl} "
        sql += f"WHERE ZWORKCD = {dbField(strZWorkCd)}"
        return SqlExecute(sql)
    except psycopg2.OperationalError as e:
        raise PostgresException(Error=e, DbTbl="TBZWORK" + strProcTbl, SqlStr=sql)


def TxtOutSkCd_CodeCheck(request, TbInlandData, strProcTbl):
    outInlandData = {}
    WkDFlg = 0
    SqlStr = ""
    try:
        for i in range(len(TbInlandData)):
            if TbInlandData[i]["inlandcd"] == request.context["TxtOutSkCd"]:
                outInlandData["InlandCd"] = request.context["TxtOutSkCd"]
                outInlandData["InlandNm"] = TbInlandData[i]["inlandnm"]
                WkDFlg = 1
                break
        if WkDFlg == 0:
            SqlStr = "SELECT INLANDNM "
            SqlStr += f"FROM TBINLAND{strProcTbl} WHERE "
            SqlStr += f"INLANDCD = {dbField(request.context['TxtOutSkCd'])}"
            RsInland = SqlExecute(SqlStr).all()
            if not RsInland.Rows:
                MsgDspWarning(request, "搬入出先テーブル", "搬入出先テーブルに該当データがありませんでした。")
                request.context["gSetField"] = "TxtOutSkCd"
                return False
            WkCnt = len(TbInlandData)
            TbInlandData[WkCnt]["inlandcd"] = request.context["TxtFwdCd"]
            TbInlandData[WkCnt]["inlandnm"] = DbDataChange(RsInland.Rows[0]["inlandnm"])
            outInlandData["InlandCd"] = request.context["TxtOutSkCd"]
            outInlandData["InlandNm"] = DbDataChange(RsInland.Rows[0]["inlandnm"])
        return True
    except psycopg2.OperationalError as e:
        raise PostgresException(Error=e, DbTbl="搬入出先テーブル", SqlStr=SqlStr)


def Cm_TbShipSchChk(strProcTbl, strVesselCd, strVoyNo):
    sql = ""
    try:
        sql = "SELECT VESSELNM,ATA,OPECD,CPORTCD,ETA "
        sql += f"FROM TBSHIPSCH{strProcTbl} "
        sql += f"WHERE VESSELCD = {dbField(strVesselCd)}"
        sql += f" AND VOYNO = {dbField(strVoyNo)}"
        return SqlExecute(sql)
    except psycopg2.OperationalError as e:
        raise PostgresException(Error=e, DbTbl="TBSHIPSCH" + strProcTbl, SqlStr=sql)


def inpdatechk(strDate, format="%Y/%m/%d"):
    try:
        res = bool(datetime.strptime(strDate, format).date())
        if res:
            return NOMAL_OK
    except ValueError:
        return FATAL_ERR
    return FATAL_ERR
