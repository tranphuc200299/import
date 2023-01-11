from main.common.function.Const import DI_MARK_PPR, DI_SAGYO_PPR, DI_KYOKA_PPR, DI_SAGYO_KSP, DI_MARK_KSP, DI_KYOKA_KSP
from main.common.function.Common import dbField
from main.common.function.DspMessage import *


def DiPrtCntl(request, PrtMode, CtDat, NaDat, KyokaDat, ChgDat, MinTonDat):
    try:
        NaCNT = len(NaDat)
        KyoCnt = len(KyokaDat)
        ChgCnt = len(ChgDat)
        if PrtMode == 0:
            MaxMark = DI_MARK_PPR
            MaxSagyo = DI_SAGYO_PPR
            MaxKyoka = DI_KYOKA_PPR
        elif PrtMode == 1:
            MaxMark = DI_MARK_KSP
            MaxSagyo = DI_SAGYO_KSP
            MaxKyoka = DI_KYOKA_KSP
        else:
            MsgDspError(request, "パラメータ(プリンタ種別)エラーです。", "D/I Make process internal error")
            return ""
        MarkCnt, HinmokuCnt, TempRemark, TempMark, TempHinmoku, page_data_clr = MultiLineControl(CtDat, NaDat, MinTonDat)
        LastPage = PageComp(MarkCnt, HinmokuCnt, MaxMark, MaxSagyo, ChgCnt, KyoCnt, MaxKyoka, NaCNT)
        page_data_clr = ChgFree(ChgDat, page_data_clr)
        dataDiPrtCntl = MakeDI(request, CtDat, NaDat, KyokaDat, ChgDat, LastPage, MaxMark, MarkCnt, TempMark, HinmokuCnt, TempHinmoku,
                               TempRemark, MaxSagyo, ChgCnt, MaxKyoka, KyoCnt, page_data_clr)
        if not dataDiPrtCntl:
            return "", dataDiPrtCntl
        elif PrtMode == 0:
            return "\DiPrtPPR.rpt", dataDiPrtCntl
        else:
            return "\DiPrtKSP.rpt", dataDiPrtCntl

    except Exception as Err:
        MsgDspError(request, "Visual Basic Error:" + str(Err), "D/I Make process internal error")


def MultiLineControl(CtDat, NaDat, MinTonDat):
    TempMark = [""]
    TempHinmoku = [""]
    TempRemark = []
    page_data_clr = PageDataClr()
    HinmokuCnt = 0
    MarkCnt = 0
    if CtDat.Mark != "":
        TempMark = CtDat.Mark.split("\n")
        MarkCnt = len(TempMark)
    if CtDat.Hinmoku != "":
        TempHinmoku = CtDat.Hinmoku.split("\n")
        HinmokuCnt = len(TempHinmoku) - 1
    page_data_clr["PrtKPackg"] = NaDat[0].KPackg
    page_data_clr["PrtWPackg"] = NaDat[0].WPackg
    page_data_clr["PrtMPackg"] = NaDat[0].MPackg
    page_data_clr["PrtRPackg"] = NaDat[0].RPackg
    WkStr = CtDat.Biko35 + "\n\n"
    for ix in range(len(NaDat)):
        if NaDat[ix].Remark != "":
            WkStr += NaDat[ix].Remark + "\n\n"
        page_data_clr["PrtKosu"] += NaDat[ix].Kosu
        if NaDat[ix].KPackg != page_data_clr["PrtKPackg"]:
            page_data_clr["PrtKPackg"] = "PKG"
        page_data_clr["PrtWeight"] += NaDat[ix].Weight
        if NaDat[ix].WPackg != page_data_clr["PrtWPackg"]:
            page_data_clr["PrtWPackg"] = "PKG"
        page_data_clr["PrtMeasur"] += NaDat[ix].Measur
        if NaDat[ix].MPackg != page_data_clr["PrtMPackg"]:
            page_data_clr["PrtMPackg"] = "PKG"
        page_data_clr["PrtRynTon"] += NaDat[ix].RynTon
        if NaDat[ix].RPackg != page_data_clr["PrtRPackg"]:
            page_data_clr["PrtRPackg"] = "PKG"
        page_data_clr["PrtMotoKosu"] += NaDat[ix].HKosu
        if NaDat[ix].HKPackg != page_data_clr["PrtMotoKpackg"]:
            page_data_clr["PrtMotoKpackg"] = NaDat[ix].HKPackg
    if page_data_clr["PrtRynTon"] < MinTonDat.MinTon:
        page_data_clr["PrtRynTon"] = MinTonDat.MinTon
    if len(WkStr) > 4:
        WkStr = WkStr[: len(WkStr) - 4]
    if WkStr != "":
        TempRemark = WkStr.split("\n")
    return MarkCnt, HinmokuCnt, TempRemark, TempMark, TempHinmoku, page_data_clr


def PageComp(MarkCnt, HinmokuCnt, MaxMark, MaxSagyo, ChgCnt, KyoCnt, MaxKyoka, NaCNT):
    WkGrp3Na = 0
    if MarkCnt > HinmokuCnt:
        WkMarkCnt = MarkCnt
    else:
        WkMarkCnt = HinmokuCnt
    WkGrp1 = int((WkMarkCnt + 1) / MaxMark)
    if (WkMarkCnt + 1) != WkGrp1 * MaxMark:
        WkGrp1 = WkGrp1 + 1
    WkChgCnt = ChgCnt
    WkGrp2 = int((WkChgCnt + 1) / MaxSagyo)
    if (WkChgCnt + 1) != WkGrp2 * MaxSagyo:
        WkGrp2 = WkGrp2 + 1
    if ChgCnt == 0:
        WkGrp2 = 1
    WkKyoCnt = KyoCnt
    WkGrp3 = int((WkKyoCnt + 1) / MaxKyoka)
    if (WkKyoCnt + 1) != WkGrp3 * MaxKyoka:
        WkGrp3 += 1
    if KyoCnt == 0:
        WkGrp3 = 1
        WkGrp3Na = int((NaCNT + 1) / MaxKyoka)
        if (NaCNT + 1) != WkGrp3Na * MaxKyoka:
            WkGrp3Na += 1
    if WkGrp1 > WkGrp2:
        LastPage = WkGrp1
    else:
        LastPage = WkGrp2
    if WkGrp3 > LastPage:
        LastPage = WkGrp3
    if WkKyoCnt == 0:
        LastPage = WkGrp3Na
    return LastPage


def ChgFree(ChDat, page_data_clr):
    for ix in range(len(ChDat)):
        if ChDat[ix].Nissu > 0:
            page_data_clr["PrtDays"] = ChDat[ix].Nissu
        page_data_clr["PrtTotal"] += ChDat[ix].Kingaku
    return page_data_clr


def MakeDI(request, CtDat, NaDat, KyokaDat, ChDat, LastPage, MaxMark, MarkCnt, TempMark, HinmokuCnt, TempHinmoku, TempRemark,
           MaxSagyo, ChgCnt, MaxKyoka, KyoCnt, page_data_clr):
    dataDiPrtCntl = []
    count = 1
    for pcnt in range(LastPage):
        intStart = MaxMark * pcnt
        intEnd = MaxMark * pcnt + MaxMark - 1
        for ix in range(intStart, intEnd):
            if MarkCnt >= ix:
                page_data_clr["PrtMark"] += TempMark[ix] + "\n"
            if HinmokuCnt >= ix:
                page_data_clr["PrtHinmoku"] += TempHinmoku[ix] + "\n"
            if len(TempRemark) > ix:
                page_data_clr["PrtRemark"] += TempRemark[ix] + "\n"
        intStart = MaxSagyo * pcnt
        intEnd = MaxSagyo * pcnt + MaxSagyo - 1
        for ix in range(intStart, intEnd):
            if ChgCnt >= ix:
                page_data_clr["PrtZWorkNm"] += ChDat[ix].ZWorkNm + "\n"
                page_data_clr["PrtNissu"] += str(round(ChDat[ix].Nissu)) + "\n"
                page_data_clr["PrtQuantity"] += f"{ChDat[ix].Quantity:,.3f}" + " " + ChDat[ix].QPackg + " " * (
                        5 - len(ChDat[ix].QPackg)) + "\n"
                if ChDat[ix].ZWorkNm == "":
                    page_data_clr["PrtTanka"] += "\n"
                    page_data_clr["PrtKingaku"] += "\n"
                else:
                    page_data_clr["PrtTanka"] += "\\" + f"{ChDat[ix].TANKA:,}" + "\n"
                    page_data_clr["PrtKingaku"] += "\\" + f"{ChDat[ix].Kingaku:,}" + "\n"
                page_data_clr["PrtSubTtl"] += ChDat[ix].Kingaku
        intStart = MaxKyoka * pcnt
        intEnd = MaxKyoka * pcnt + MaxKyoka - 1
        for ix in range(intStart, intEnd):
            if KyoCnt >= ix:
                page_data_clr["PrtNaBlNo"] += KyokaDat[ix].NaBlNo + "\n"
                page_data_clr["PrtPrmSybt"] += KyokaDat[ix].OutPrmSybt + "\n"
                page_data_clr["PrtPrmNo"] += KyokaDat[ix].OutPrmNo + "\n"
                page_data_clr["PrtPrmDate"] += KyokaDat[ix].OutPrmDate + "\n"
        if KyoCnt == 0:
            PrtNaBlNo = ""
            intStart = MaxKyoka * pcnt
            intEnd = MaxKyoka * pcnt + MaxKyoka - 1
            for ix in range(intStart, intEnd):
                if len(NaDat) > ix:
                    PrtNaBlNo = PrtNaBlNo + NaDat[ix].NaBlNo + "\n"
        if page_data_clr["PrtMotoKosu"] == 0:
            page_data_clr["PrtMotoKosu"] = page_data_clr["PrtKosu"]
            page_data_clr["PrtMotoKpackg"] = page_data_clr["PrtKPackg"]
        result = InsDI(request, CtDat, page_data_clr, count)
        if not result:
            return False
        count += 1
        dataDiPrtCntl.append(result)
        page_data_clr = PageDataClr()
    return dataDiPrtCntl


def InsDI(request, CtDat, page_data_clr, count):
    try:
        result = {
            "sVesselNm": CtDat.VesselNm,
            "sVoyNo": dbField(CtDat.VoyNo),
            "sCtBlNo": dbField(CtDat.CtBlNo),
            "nSeq": count,
            "sFwdNm": dbField(CtDat.FwdNm),
            "sBillNo": dbField(CtDat.BillNo),
            "sAllRDate": dbField(CtDat.InDate),
            "sZPlace": dbField(CtDat.ZPlace),
            "sAPortCd": dbField(CtDat.PodNm),
            "sMarks": dbField(page_data_clr["PrtMark"]),
            "sHinmoku": dbField(page_data_clr["PrtHinmoku"]),
            "sRemark": dbField(page_data_clr["PrtRemark"]),
            "nKosu": page_data_clr["PrtKosu"],
            "sKPackg": dbField(page_data_clr["PrtKPackg"]),
            "sATA": dbField(CtDat.Arrive),
            "sFreeNdDt": dbField(CtDat.FreeEndDate),
            "sOutDate": dbField(CtDat.DelvDate),
            "nOverDay": dbField(page_data_clr["PrtDays"]),
            "nWeight": page_data_clr["PrtWeight"],
            "sWPackg": dbField(page_data_clr["PrtWPackg"]),
            "nMeasur": page_data_clr["PrtMeasur"],
            "sMPackg": dbField(page_data_clr["PrtMPackg"]),
            "nRynTon": page_data_clr["PrtRynTon"],
            "sRPackg": dbField(page_data_clr["PrtRPackg"]),
            "sZWorkNm": dbField(page_data_clr["PrtZWorkNm"]),
            "sDemuNisu": dbField(page_data_clr["PrtNissu"]),
            "sKsorkt": dbField(page_data_clr["PrtQuantity"]),
            "sTanka": dbField(page_data_clr["PrtTanka"]),
            "sKingaku": dbField(page_data_clr["PrtKingaku"]),
            "sNaBlNo": dbField(page_data_clr["PrtNaBlNo"]),
            "sOutPrmSybt": dbField(page_data_clr["PrtPrmSybt"]),
            "sOutPrmNo": dbField(page_data_clr["PrtPrmNo"]),
            "sOutPrmDate": dbField(page_data_clr["PrtPrmDate"]),
            "sCompanyNm": dbField(CtDat.Company),
            "sBranchNm": dbField(CtDat.Branch),
            "sJimusyoNm": dbField(CtDat.Jimusyo),
            "sMotoKosu": page_data_clr["PrtMotoKosu"],
            "sMotoPackg": dbField(page_data_clr["PrtMotoKpackg"]),
            "nSubTTL": page_data_clr["PrtSubTtl"],
            "nKinTotal": page_data_clr["PrtTotal"]
        }
        return result
    except Exception as Err:
        MsgDspError(request, "Local D/B Insert Error", "Visual Basic Error:" + str(Err))
        return False


def PageDataClr():
    page_data_clr = {}
    page_data_clr["PrtKosu"] = 0
    page_data_clr["PrtKPackg"] = ""
    page_data_clr["PrtWeight"] = 0
    page_data_clr["PrtWPackg"] = ""
    page_data_clr["PrtMeasur"] = 0
    page_data_clr["PrtMPackg"] = ""
    page_data_clr["PrtRynTon"] = 0
    page_data_clr["PrtRPackg"] = ""
    page_data_clr["PrtMotoKosu"] = 0
    page_data_clr["PrtMotoKpackg"] = ""
    page_data_clr["PrtDays"] = 0
    page_data_clr["PrtMark"] = ""
    page_data_clr["PrtHinmoku"] = ""
    page_data_clr["PrtRemark"] = ""
    page_data_clr["PrtZWorkNm"] = ""
    page_data_clr["PrtNissu"] = ""
    page_data_clr["PrtQuantity"] = ""
    page_data_clr["PrtTanka"] = ""
    page_data_clr["PrtKingaku"] = ""
    page_data_clr["PrtNaBlNo"] = ""
    page_data_clr["PrtPrmSybt"] = ""
    page_data_clr["PrtPrmNo"] = ""
    page_data_clr["PrtPrmDate"] = ""
    page_data_clr["PrtSubTtl"] = 0
    page_data_clr["PrtTotal"] = 0
    return page_data_clr
