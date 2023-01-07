import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from main.common.function import SqlExecute
from django.db import IntegrityError, transaction
from main.common.function.Const import DB_FATAL_ERR, DB_TBFREETM_NOT_FIND, DB_TBCALENDER_NOT_FIND, csFKISANKBN_1, csFCALC_1, \
    csFCALC_3, csDAYKBN_3, TRACK_VANNO, NOMAL_OK, FATAL_ERR, DB_TBOPE_NOT_FIND, DB_NOMAL_OK, csDEMUCKBN_A, csDEMUCKBN_C, \
    DB_TBDEMURG_NOT_FIND, csMTONTKBN_1, csMTONTKBN_2, csMTONTKBN_3, csDCALC_1, csDAYKBN_1, \
    csDAYKBN_2, csDCALC_3, csDAYKBN_9, csDAYKBN_4, csLOCK_ON, DB_NOT_FIND, DB_LOCK, csSTANKAKBN_1, csSTANKAKBN_2, csSTANKAKBN_3, \
    csSTANKAKBN_4, csSTANKAKBN_5
from main.middleware.exception.exceptions import RuntimeException
from middleware.exception.message import E00001
from time import sleep

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
        RsCalen = SqlExecute(SqlStr).all()
        if not RsCalen.Rows:
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
            WkKDateY = CmfDateFmt((datetime.strptime(KDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%Y")
            WkKDateM = CmfDateFmt((datetime.strptime(KDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%m")
            WkKDateD = CmfDateFmt((datetime.strptime(KDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%d")
            WkFreeTime = ""
            if WkFCALC == csFCALC_3:
                WkKDate = WkKDateY + "/" + WkKDateM + "/" + WkKDateD
            else:
                WkKDate = ""
                for i in range(len(RsFreeTm.Rows)):
                    if WkKDate != "":
                        break
                    if tbcalen[i]["YMDATE"] == WkKDateY + "/" + WkKDateM:
                        day_kbn = tbcalen[i]["DAYKBN"][int(WkKDateD) - 1]
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
                        if WkKDateD == "32" or tbcalen[i]["DAYKBN"][int(WkKDateD) - 1] == csDAYKBN_9:
                            WkKDate = WkKDateY + "/" + WkKDateM + "/01"
                            WkKDateY = CmfDateFmt(
                                (datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%Y")
                            WkKDateM = CmfDateFmt(
                                (datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%m")
                            WkKDateD = CmfDateFmt(
                                (datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%d")
                            WkKDate = ""
                            continue
                    else:
                        WkKDate = ""
                if WkKDate == "":
                    return DB_TBCALENDER_NOT_FIND
        if WkFCALC == csFCALC_3 or WkFDAYS == 0:
            WkFreeTime = CmfDateFmt((datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=WkFDAYS)).strftime("%Y/%m/%d"),
                                    "%Y/%m/%d")
            return WkFreeTime
        WkKDateY = CmfDateFmt((datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%Y")
        WkKDateM = CmfDateFmt((datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%m")
        WkKDateD = CmfDateFmt((datetime.strptime(WkKDate, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%d")
        WkFreeTime = ""
        WkFCnt = 0
        for i in range(len(RsFreeTm.Rows)):
            if WkFreeTime != "":
                break
            if tbcalen[i]["YMDATE"] == WkKDateY + "/" + WkKDateM:
                if tbcalen[i]["DAYKBN"][int(WkKDateD)] == csDAYKBN_9:
                    WkFreeTime = WkKDateY + "/" + WkKDateM + "/01"
                    WkKDateY = CmfDateFmt(
                        (datetime.strptime(WkFreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%Y")
                    WkKDateM = CmfDateFmt(
                        (datetime.strptime(WkFreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%m")
                    WkKDateD = CmfDateFmt(
                        (datetime.strptime(WkFreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%d")
                    WkFreeTime = ""
                    continue
                if not tbcalen[i]["YMDATE"] == WkKDateY + "/" + WkKDateM:
                    continue
                if tbcalen[i]["DAYKBN"][int(WkKDateD)] == csDAYKBN_1:
                    WkFCnt = WkFCnt + 1
                if WkFCALC == csFCALC_1 and tbcalen[i]["DAYKBN"][int(WkKDateD)] == csDAYKBN_2:
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

    except IntegrityError as ie:
        _logger.error(ie)
        return DB_FATAL_ERR


def VanDigit_Check(strVanNo):
    vntVanChr = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
                 "W", "X", "Y", "Z", "*"]
    vntVanNum = ["10", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "23", "24", "25", "26", "27", "28", "29",
                 "30", "31", "32", "34", "35", "36", "37", "38", "*"]
    if strVanNo[:3] == TRACK_VANNO:
        return NOMAL_OK
    if len(strVanNo) != 11:
        return FATAL_ERR
    for i in range(4):
        if strVanNo[i] not in vntVanChr[:-1]:
            return FATAL_ERR
    for i in range(4, 11):
        if strVanNo[i] not in vntVanNum[:-1]:
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
    try:
        sql = "SELECT HPORTCD "
        sql += f"FROM TBCFSSYS{strSelTbl} "
        sql += f"WHERE HOZEICD = {dbField(strSelHozCd)}"
        RsTbCfsSys = SqlExecute(sql).all()
        if not RsTbCfsSys.Rows:
            return ""
        else:
            return RsTbCfsSys.Rows[0]["HPORTCD"]
    except IntegrityError as ie:
        _logger.error(ie)
        raise RuntimeException(error_code=E00001, message="TBCFSSYS" + strSelTbl)


def GetDemurg(GDemurg, strSelTbl):
    try:
        WkErrTbl = "カレンダーテーブル"
        SqlStr = f"SELECT YMDATE, DAYKBN FROM TBCALENDER{strSelTbl} WHERE "
        SqlStr += f"YMDATE >= {dbField(CmfDateFmt(GDemurg.FreeTime, '%Y/%m'))}"
        SqlStr += " ORDER BY YMDATE"
        RsCalen = SqlExecute(SqlStr).all()
        if not RsCalen.Rows:
            return DB_TBCALENDER_NOT_FIND
        tbcalen = []
        for i in range(len(RsCalen.Rows)):
            tbcalen[i]["YMDATE"] = RsCalen.Rows["YMDATE"]
            tbcalen[i]["YMDATEY"] = int(RsCalen.Rows["YMDATE"][:4])
            tbcalen[i]["YMDATEM"] = int(RsCalen.Rows["YMDATE"][6:8])
            tbcalen[i]["DAYKBN"] = RsCalen.Rows["DAYKBN"]
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
        SqlStr += f"WHERE A.OPECD = {dbField(GDemurg.OpeCd)} "
        RsDemu = SqlExecute(SqlStr).all()
        if not RsDemu.Rows:
            return DB_TBOPE_NOT_FIND
        if not RsDemu.Rows[0]["OPECD2"]:
            return DB_TBDEMURG_NOT_FIND

        WkMinTon = int(RsDemu.Rows[0]["MinTon"])
        GDemurg.MinTon = int(RsDemu.Rows[0]["MinTon"])
        tbdemurg = []
        for i in range(1, 6):
            tbdemurg.append({
                "RANK": int(RsDemu.Rows[0]["RANK" + str(i)]),
                "TANKA": round(RsDemu.Rows[0]["TANKA" + str(i)])
            })
        if RsDemu.Rows[0]["STANKAKBN"] == csSTANKAKBN_2:
            WkDemurg = GDemurg.KMeasur
        elif RsDemu.Rows[0]["STANKAKBN"] == csSTANKAKBN_3:
            WkDemurg = GDemurg.KWeight / 1000
        else:
            WkDemurg = GDemurg.RynTon

        if GDemurg.MtonTKbn == csMTONTKBN_2:
            WkDemurg = WkMinTon
        elif GDemurg.MtonTKbn == csMTONTKBN_3:
            if WkMinTon > WkDemurg:
                WkDemurg = WkMinTon
        GDemurg.STANKAKBN = RsDemu.Rows[0]["STANKAKBN"]
        WkTankaC = dbLong(RsDemu.Rows[0]["TANKAC"])
        WkDCalc = RsDemu.Rows[0]["DCALC"]
        WkDateY = CmfDateFmt(
            (datetime.strptime(GDemurg.FreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%Y")
        WkDateM = CmfDateFmt(
            (datetime.strptime(GDemurg.FreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%m")
        WkDateD = CmfDateFmt(
            (datetime.strptime(GDemurg.FreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"), "%d")
        WkDate = WkDateY + "/" + WkDateM + "/" + WkDateD
        WkNisu = 0
        WkEndFlg = 0
        for i in range(len(RsCalen.Rows)):
            if WkEndFlg == 9:
                break
            day_kbn = tbcalen[i]["DAYKBN"][int(WkDateD)]
            if tbcalen[i]["YMDATE"] + "/" + f"{WkDateD:02}" > GDemurg.OutDate:
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
            if WkDateD == "32" or tbcalen[i]["DAYKBN"][int(WkDateD) - 2] == csDAYKBN_9:
                WkDate = WkDateY + "/" + WkDateM + "/01"
                WkDateY = CmfDateFmt((datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                                     "%Y")
                WkDateM = CmfDateFmt((datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                                     "%m")
                WkDateD = CmfDateFmt((datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                                     "%d")
        if WkEndFlg == 0:
            return DB_TBCALENDER_NOT_FIND
        if WkNisu == 0:
            GDemurg.demurg = 0
            return DB_NOMAL_OK
        if WkTankaC == 0:
            GDemurg.DemuCKbn = csDEMUCKBN_A
            for i in range(len(tbdemurg)):
                if WkNisu <= tbdemurg[i]["RANK"]:
                    GDemurg.DemuTanka = tbdemurg[i]["TANKA"]
                    GDemurg.demurg = tbdemurg[i]["TANKA"] * WkNisu * WkDemurg
                    GDemurg.DemurgN = WkNisu
                    break
        else:
            GDemurg.DemuCKbn = csDEMUCKBN_C
            for i in range(len(tbdemurg)):
                if WkNisu <= tbdemurg[i]["RANK"]:
                    GDemurg.CDemuTanka1 = tbdemurg[i]["TANKA"]
                    GDemurg.CDemuTanka2 = 0
                    GDemurg.demurg = tbdemurg[i]["TANKA"] * WkNisu * WkDemurg
                    GDemurg.CDemurgN1 = WkNisu
                    GDemurg.CDemurgN2 = 0
                    break
                else:
                    if i != 4:
                        if tbdemurg[i + 1]["RANK"] == 0:
                            GDemurg.CDemuTanka1 = tbdemurg[i]["TANKA"]
                            GDemurg.CDemuTanka2 = WkTankaC * (WkNisu - tbdemurg[i]["RANK"])
                            GDemurg.demurg = (tbdemurg[i]["TANKA"] * tbdemurg[i]["RANK"] * WkDemurg) + (
                                    WkTankaC * (WkNisu - tbdemurg[i]["RANK"]) * WkDemurg)
                            GDemurg.CDemurgN1 = tbdemurg[i]["RANK"]
                            GDemurg.CDemurgN2 = WkNisu - tbdemurg[i]["RANK"]
                            break
            if GDemurg.demurg == 0:
                GDemurg.CDemuTanka1 = tbdemurg[4]["TANKA"]
                GDemurg.CDemuTanka2 = WkTankaC * (WkNisu - tbdemurg[4]["RANK"])
                GDemurg.demurg = (tbdemurg[4]["TANKA"] * tbdemurg[4]["RANK"] * WkDemurg) + (
                        WkTankaC * (WkNisu - tbdemurg[4]["RANK"]) * WkDemurg)
                GDemurg.CDemurgN1 = tbdemurg[4]["RANK"]
                GDemurg.CDemurgN2 = WkNisu - tbdemurg[4]["RANK"]
        return DB_NOMAL_OK
    except:
        return DB_FATAL_ERR


def GetDemurg2(GDemurg, strSelTbl):
    try:
        WkDemurg = 0
        WkErrTbl = "カレンダーテーブル"
        SqlStr = "SELECT YMDATE, DAYKBN FROM TBCALENDER{strSelTbl} WHERE "
        SqlStr += f"YMDATE >= {dbField(CmfDateFmt(GDemurg.FreeTime, '%Y/%m'))}"
        SqlStr += " ORDER BY YMDATE"
        RsCalen = SqlExecute(SqlStr).all()
        if not RsCalen.Rows:
            return DB_TBCALENDER_NOT_FIND
        tbcalen = []
        for i in range(len(RsCalen.Rows)):
            tbcalen[i]["YMDATE"] = RsCalen.Rows[0]["YMDATE"]
            tbcalen[i]["YMDATEY"] = int(RsCalen.Rows[0]["YMDATE"][:4])
            tbcalen[i]["YMDATEM"] = int(RsCalen.Rows[0]["YMDATE"][6:8])
            tbcalen[i]["DAYKBN"] = RsCalen.Rows[0]["DAYKBN"]
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
        SqlStr += f"B.OPECD = {dbField(GDemurg.OpeCd)}"
        RsDemu = SqlExecute(SqlStr).all()
        if not RsDemu.Rows:
            return DB_TBDEMURG_NOT_FIND
        tbdemurg = []
        WkRankMax = 0
        for i in range(1, 6):
            tbdemurg.append({
                "RANK": int(RsDemu.Rows[0]["RANK" + str(i)]),
                "TANKA": round(RsDemu.Rows[0]["TANKA" + str(i)])
            })
            if WkRankMax < int(RsDemu.Rows[0]["RANK" + str(i)]):
                WkRankMax = int(RsDemu.Rows[0]["RANK" + str(i)])
        if GDemurg.MtonTKbn == csMTONTKBN_1:
            WkDemurg = GDemurg.RynTon
        elif GDemurg.MtonTKbn == csMTONTKBN_2:
            WkDemurg = GDemurg.MinTon
        elif GDemurg.MtonTKbn == csMTONTKBN_3:
            if GDemurg.RynTon > GDemurg.MinTon:
                WkDemurg = GDemurg.RynTon
            else:
                WkDemurg = GDemurg.MinTon

        WkTankaC = dbLong(RsDemu.Rows[0]["TANKAC"])
        WkDCalc = RsDemu.Rows[0]["DCALC"]
        WkDateY = CmfDateFmt((datetime.strptime(GDemurg.FreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
                             "%Y")
        WkDateM = CmfDateFmt((datetime.strptime(GDemurg.FreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
                             "%m")
        WkDateD = CmfDateFmt((datetime.strptime(GDemurg.FreeTime, "%Y/%m/%d") + relativedelta(days=1)).strftime("%Y/%m/%d"),
                             "%d")
        WkDate = WkDateY + "/" + WkDateM + "/" + WkDateD
        WkNisu = 0
        WkEndFlg = 0
        for i in range(len(RsCalen.Rows)):
            if WkEndFlg == 9:
                break
            if tbcalen[i]["YMDATE"] >= WkDateY + "/" + WkDateM:
                WkEndFlg = 9
            day_kbn = tbcalen[i]["DAYKBN"][int(WkDateD)]
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
            if WkDateD == "32" or tbcalen[i]["DAYKBN"][int(WkDateD) - 2] == csDAYKBN_9:
                WkDate = WkDateY + "/" + WkDateM + "/01"
                WkDateY = CmfDateFmt((datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                                     "%Y")
                WkDateM = CmfDateFmt((datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                                     "%m")
                WkDateD = CmfDateFmt((datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                                     "%d")

        if WkEndFlg == 0:
            return DB_TBCALENDER_NOT_FIND
        if WkNisu == 0:
            GDemurg.demurg = 0
            GDemurg.DemurgN = 0
            return DB_NOMAL_OK
        if WkTankaC == 0:
            GDemurg.DemuCKbn = csDEMUCKBN_A
            for i in range(len(tbdemurg)):
                if WkNisu <= tbdemurg[i]["RANK"]:
                    GDemurg.DemuTanka = tbdemurg[i]["TANKA"]
                    GDemurg.demurg = f"{tbdemurg[i]['TANKA'] * WkNisu * WkDemurg :01}"
                    GDemurg.DemurgN = WkNisu
                    break
                else:
                    if WkRankMax == tbdemurg[i]["RANK"]:
                        if WkNisu >= tbdemurg[i]["RANK"]:
                            GDemurg.DemuTanka = tbdemurg[i]["TANKA"]
                            GDemurg.demurg = f"{tbdemurg[i]['TANKA'] * WkNisu * WkDemurg :01}"
                            GDemurg.DemurgN = WkNisu
                            break
        else:
            GDemurg.DemuCKbn = csDEMUCKBN_C
            for i in range(len(tbdemurg)):
                if WkNisu <= tbdemurg[i]["RANK"]:
                    GDemurg.CDemuTanka1 = tbdemurg[i]["TANKA"]
                    GDemurg.CDemuTanka2 = 0
                    GDemurg.demurg = f"{tbdemurg[i]['TANKA'] * WkNisu * WkDemurg :01}"
                    GDemurg.CDemurgN1 = WkNisu
                    GDemurg.CDemurgN2 = 0
                else:
                    if i != 4:
                        if tbdemurg[i + 1]["RANK"] == 0:
                            GDemurg.CDemuTanka1 = tbdemurg[i]["TANKA"]
                            GDemurg.CDemuTanka2 = WkTankaC * (WkNisu - tbdemurg[i]["RANK"])
                            GDemurg.demurg = f"{(tbdemurg[i]['TANKA'] * tbdemurg[i]['RANK'] * WkDemurg) + (WkTankaC * (WkNisu - tbdemurg[i]['RANK']) * WkDemurg) :01}"
                            GDemurg.CDemurgN1 = tbdemurg[i]["RANK"]
                            GDemurg.CDemurgN2 = WkNisu - tbdemurg[i]["RANK"]
                            break

            if GDemurg.demurg == 0:
                GDemurg.CDemuTanka1 = tbdemurg[4]["TANKA"]
                GDemurg.CDemuTanka2 = WkTankaC * (WkNisu - tbdemurg[4]["RANK"])
                GDemurg.demurg = f"{(tbdemurg[4]['TANKA'] * tbdemurg[4]['RANK'] * WkDemurg) + (WkTankaC * (WkNisu - tbdemurg[4]['RANK']) * WkDemurg) :01}"
                GDemurg.CDemurgN1 = tbdemurg[4]["RANK"]
                GDemurg.CDemurgN2 = WkNisu - tbdemurg[4]["RANK"]
        return DB_NOMAL_OK
    except:
        return DB_FATAL_ERR


def GetSeikyuNo(ProgramId, SystemData, SeikyuNo, iniUpdCd, iniUpdTbl, iniWsNo):
    try:
        NowDate = ""
        GetFlg = 0
        for i in range(11):
            status, NowDate = TbCfsSysSELECT(SystemData, csLOCK_ON, iniUpdCd, iniUpdTbl)
            if status == DB_NOMAL_OK:
                GetFlg = 1
                break
            elif status == DB_LOCK:
                GetFlg = 0
            else:
                # Call OraErrorH("CFSシステムテーブル", SqlStr)
                return DB_FATAL_ERR
            sleep(1)

        if GetFlg == 0:
            return DB_LOCK
        SeikyuHead = SystemData.SEIKYUHNO[:6]
        if SeikyuHead == NowDate[:6]:
            SeikyuSeq = round(float(SystemData.SEIKYUHNO[6:11])) + 1
        else:
            SeikyuHead = NowDate[:6]
            SeikyuSeq = 1
        SystemData.SEIKYUHNO = f"{SeikyuHead:@6}" + f"{SeikyuSeq:04}"
        SeikyuNo = SystemData.SEIKYUHNO
        with transaction.atomic():
            SqlStr = "UPDATE TBCFSSYS{strSelTbl} SET "
            SqlStr += f"SEIKYUHNO = {dbField(SystemData.SEIKYUHNO)}, "
            SqlStr += "UDATE = SYSDATE, "
            SqlStr += f"UPROGID = {dbField(ProgramId)}, "
            SqlStr += f"UWSID = {dbField(iniWsNo)}"
            SqlStr += f" WHERE HOZEICD = {dbField(SystemData.HOZEICD)}"
            SqlExecute(SqlStr).execute()
        return DB_NOMAL_OK
    except:
        # Call OraErrorH("CFSシステムテーブル", SqlStr)
        return DB_FATAL_ERR


def TbCfsSysSELECT(SystemData, LockKbn, iniUpdCd, iniUpdTbl):
    try:
        for i in range(len(iniUpdCd)):
            if iniUpdCd(i) == SystemData.HOZEICD:
                WkTblKbn = iniUpdTbl(i)
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
        SqlStr += "SEIKYUHNO, "
        SqlStr += "TO_CHAR(SYSDATE,'YYYYMMDD') AS NOWDATE "
        SqlStr += f"FROM TBCFSSYS{WkTblKbn}"
        SqlStr += " WHERE "
        SqlStr += f"HOZEICD = {dbField(SystemData.HOZEICD)}"
        if LockKbn == csLOCK_ON:
            SqlStr += " FOR UPDATE NOWAIT"
        RsSys = SqlExecute(SqlStr).all()
        if not RsSys.Rows:
            return DB_NOT_FIND
        SystemData.COMPANYNM = DbDataChange(RsSys.Rows[0]["COMPANYNM"])
        SystemData.BRANCHNM = DbDataChange(RsSys.Rows[0]["BRANCHNM"])
        SystemData.JIMUSYCD = DbDataChange(RsSys.Rows[0]["JIMUSYCD"])
        SystemData.JIMUSYNM = DbDataChange(RsSys.Rows[0]["JIMUSYNM"])
        SystemData.JIMUSYADR = DbDataChange(RsSys.Rows[0]["JIMUSYADR"])
        SystemData.JIMUSYTEL = DbDataChange(RsSys.Rows[0]["JIMUSYTEL"])
        SystemData.JIMUSYFAX = DbDataChange(RsSys.Rows[0]["JIMUSYFAX"])
        SystemData.KEIJIMSG = DbDataChange(RsSys.Rows[0]["KEIJIMSG"])
        SystemData.HPORTCD = DbDataChange(RsSys.Rows[0]["HPORTCD"])
        SystemData.HOZEINM = DbDataChange(RsSys.Rows[0]["HOZEINM"])
        SystemData.GWSKBN = DbDataChange(RsSys.Rows[0]["GWSKBN"])
        SystemData.GW1IP = DbDataChange(RsSys.Rows[0]["GW1IP"])
        SystemData.GW1USERID = DbDataChange(RsSys.Rows[0]["GW1USERID"])
        SystemData.GW1PASSWD = DbDataChange(RsSys.Rows[0]["GW1PASSWD"])
        SystemData.GW1NAME = DbDataChange(RsSys.Rows[0]["GW1NAME"])
        SystemData.GW1SDIR = DbDataChange(RsSys.Rows[0]["GW1SDIR"])
        SystemData.GW2IP = DbDataChange(RsSys.Rows[0]["GW2IP"])
        SystemData.GW2USERID = DbDataChange(RsSys.Rows[0]["GW2USERID"])
        SystemData.GW2PASSWD = DbDataChange(RsSys.Rows[0]["GW2PASSWD"])
        SystemData.GW2NAME = DbDataChange(RsSys.Rows[0]["GW2NAME"])
        SystemData.GW2SDIR = DbDataChange(RsSys.Rows[0]["GW2SDIR"])
        SystemData.USERCD = DbDataChange(RsSys.Rows[0]["USERCD"])
        SystemData.IDCD1 = DbDataChange(RsSys.Rows[0]["IDCD1"])
        SystemData.USERPSWD1 = DbDataChange(RsSys.Rows[0]["USERPSWD1"])
        SystemData.IDCD2 = DbDataChange(RsSys.Rows[0]["IDCD2"])
        SystemData.USERPSWD2 = DbDataChange(RsSys.Rows[0]["USERPSWD2"])
        SystemData.IOJNOHEAD = DbDataChange(RsSys.Rows[0]["IOJNOHEAD"])
        SystemData.IOJNOMIN = DbDataChange(RsSys.Rows[0]["IOJNOMIN"])
        SystemData.IOJNOMAX = DbDataChange(RsSys.Rows[0]["IOJNOMAX"])
        SystemData.IOJNONOW = DbDataChange(RsSys.Rows[0]["IOJNONOW"])
        SystemData.UNQFILENM = DbDataChange(RsSys.Rows[0]["UNQFILENM"])
        SystemData.TAXNEW = DbDataChange(RsSys.Rows[0]["TAXNEW"])
        SystemData.TAXOLD = DbDataChange(RsSys.Rows[0]["TAXOLD"])
        SystemData.TAXCHG = DbDataChange(RsSys.Rows[0]["TAXCHG"])
        SystemData.GENGONEW = DbDataChange(RsSys.Rows[0]["GENGONEW"])
        SystemData.GENGOOLD = DbDataChange(RsSys.Rows[0]["GENGOOLD"])
        SystemData.GENGOCHG = DbDataChange(RsSys.Rows[0]["GENGOCHG"])
        SystemData.SEIKYUHNO = DbDataChange(RsSys.Rows[0]["SEIKYUHNO"])
        NowDate = DbDataChange(RsSys.Rows[0]["NowDate"])
        return DB_NOMAL_OK, NowDate


    except:
        if OraDbH.LastServerErr == 54:
            return DB_LOCK, None
        else:
            # Call OraErrorH("CFSシステムテーブル", SqlStr)
            return DB_FATAL_ERR, None


def DbDataChange(DbStr):
    if not DbStr or DbStr == chr(0):
        return ""
    return DbStr


def GetRevenue(OpeCd, KGWeight, M3Measur, RynDataCnt, RynData, strSelTbl):
    try:
        WkSTankaKbn = ""
        if RynDataCnt == 0:
            RynData = []
        else:
            for i in range(len(RynData)):
                if RynData[i].OpeCd == OpeCd:
                    WkSTankaKbn = RynData(i).STANKAKBN
                    MinTon = RynData[i].MinTon
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
            RynDataCnt = RynDataCnt + 1
            RynData[- 1].OpeCd = OpeCd
            RynData[- 1].STANKAKBN = DbDataChange(RsDb.Rows[0]["STANKAKBN"])
            RynData[- 1].MinTon = int(DbDataChange(RsDb.Rows[0]["MinTon"]))
            WkSTankaKbn = DbDataChange(RsDb.Rows[0]["STANKAKBN"])
            MinTon = int(DbDataChange(RsDb.Rows[0]["MinTon"]))

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
        return DB_NOMAL_OK, RynTon, MinTon,
    except:
        # Call OraError(WkErrTbl, SqlStr)
        return DB_FATAL_ERR, None, None


def GetDemurgKDate(OpeCd, FreeTime, strSelTbl, WkDCalc):
    try:
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
        for i in range(len(RsCalen.Rows)):
            tbcalen[i]["YMDATE"] = RsCalen.Rows[0]["YMDATE"]
            tbcalen[i]["YMDATEY"] = int(RsCalen.Rows[0]["YMDATE"][:4])
            tbcalen[i]["YMDATEM"] = int(RsCalen.Rows[0]["YMDATE"][6:8])
            tbcalen[i]["DAYKBN"] = RsCalen.Rows[0]["DAYKBN"]
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
        for i in range(len(RsDemu.Rows)):
            if WkEndFlg == 9:
                break
            day_kbn = tbcalen[i]["DAYKBN"][int(WkDateD)]
            if day_kbn == csDAYKBN_2:
                if WkDCalc in [csDCALC_1, csDCALC_3]:
                    GetDemurgKDate = tbcalen[i]["YMDATE"] + "/" + WkDateD
                    WkEndFlg = 9
                    continue
            elif day_kbn in [csDAYKBN_3, csDAYKBN_4]:
                if WkDCalc == csDCALC_3:
                    GetDemurgKDate = tbcalen[i]["YMDATE"] + "/" + WkDateD
                    WkEndFlg = 9
                    continue
            elif day_kbn == csDAYKBN_9:
                pass
            else:
                GetDemurgKDate = tbcalen[i]["YMDATE"] + "/" + WkDateD
                WkEndFlg = 9
            WkDateD = f"{int(WkDateD) + 1 :02}"
            if WkDateD == "32" or tbcalen[i]["DAYKBN"][int(WkDateD) - 2] == csDAYKBN_9:
                WkDate = WkDateY + "/" + WkDateM + "/01"
                WkDateY = CmfDateFmt((datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                                     "%Y")
                WkDateM = CmfDateFmt((datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                                     "%m")
                WkDateD = CmfDateFmt((datetime.strptime(WkDate, "%Y/%m/%d") + relativedelta(months=1)).strftime("%Y/%m/%d"),
                                     "%d")
                WkDate = ""
        return GetDemurgKDate

    except:
        return DB_FATAL_ERR
