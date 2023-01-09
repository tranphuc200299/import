from time import sleep
from datetime import datetime, timedelta
from django.db import transaction
from main.common.function.Const import FATAL_ERR, csLOCK_ON, DB_NOMAL_OK, DB_LOCK, NOMAL_OK, csGWSKBN_9, FILENM_SND, FILENM_TMP, \
    FTPFILE, FTPLOGFILE, FTPBATFILE, FTPFNDFILE, FTPENDFILE
from main.common.function.Common import TbCfsSysSELECT, dbField
import os

dir_path = os.path.dirname(os.path.realpath(__file__))


def NacUniqGet(strUProGId, SystemData, strUnqFileNm, strIoJNo, iniUpdCd, iniUpdTbl, iniWsNo, strSelHozCd):
    try:
        intDataGet = 0
        for intCnt in range(11):
            tb_cfs_sys = TbCfsSysSELECT(SystemData, csLOCK_ON, iniUpdCd, iniUpdTbl)
            if tb_cfs_sys == DB_NOMAL_OK:
                intDataGet = 1
                break
            elif tb_cfs_sys == DB_LOCK:
                intDataGet = 0
            else:
                return FATAL_ERR
            sleep(1)
        if intDataGet == 0:
            return DB_LOCK
        strNowDate = datetime.now()
        strUnqFileNm = datetime.strptime(SystemData.UNQFILENM, "%Y/%m/%d %H:%M:%S")
        if strUnqFileNm < strNowDate:
            strUnqFileNm = (strNowDate + timedelta(seconds=1)).strftime("%Y/%m/%d %H:%M:%S")
        else:
            strUnqFileNm = (strUnqFileNm + timedelta(seconds=1)).strftime("%Y/%m/%d %H:%M:%S")
        lngIoJNo = SystemData.IOJNONOW + 1
        if lngIoJNo > SystemData.IOJNOMAX:
            lngIoJNo = SystemData.IOJNOMIN
        strIoJNo = SystemData.IOJNOHEAD + f"{lngIoJNo:08}"
        with transaction.atomic():
            sql = "UPDATE TBCFSSYS{strSelTbl} "
            sql += f"SET IOJNONOW = {lngIoJNo},"
            sql += f"UNQFILENM = {dbField(strUnqFileNm)},"
            sql += f"UDATE = SYSDATE,"
            sql += f"UPROGID = {dbField(strUProGId)},"
            sql += f"UWSID = {dbField(iniWsNo)} "
            sql += f"WHERE HOZEICD = {dbField(strSelHozCd)}"

        return NOMAL_OK
    except:
        # OraErrorH "TBCFSSYS" & strSelTbl, sql
        return FATAL_ERR


def NacHdrSet(strNacGymCd, strUserCd, strIdCd, strUserPswd, strIoJNo):
    try:
        intLen = len(strNacGymCd)
        strNacHdr = "   " + "".join(strNacGymCd) + " " * (5 - intLen) + " " * 21
        intLen = len(strUserCd)
        strNacHdr += "".join(strUserCd) + " " * (5 - intLen)
        intLen = len(strIdCd)
        strNacHdr += "".join(strIdCd) + " " * (3 - intLen)
        intLen = len(strUserPswd)
        strNacHdr += "".join(strUserPswd) + " " * (8 - intLen)
        strNacHdr += " " * 208
        intLen = len(strIoJNo)
        strNacHdr += "".join(strIoJNo) + " " * (10 - intLen)
        strNacHdr += " " * 101
        strNacHdr += "2"
        strNacHdr += " " * 33
        return NOMAL_OK
    except:
        return FATAL_ERR


def NacFtpPut(SystemData, strSndFilePath, strSndFileNm):
    try:
        if SystemData.GWSKBN == csGWSKBN_9:
            return NOMAL_OK
        strSndFile_Snd = strSndFileNm & FILENM_SND
        strSndFile_Tmp = strSndFileNm & FILENM_TMP
        strCurrentFolder = dir_path
        for file in [FTPFILE, FTPLOGFILE, FTPBATFILE, FTPFNDFILE, FTPENDFILE]:
            if os.path.exists(file):
                os.remove(file)
    except:
        return FATAL_ERR
