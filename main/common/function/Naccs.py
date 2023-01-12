import os
from time import sleep
from datetime import datetime, timedelta
from django.db import transaction
import psycopg2
from main.common.function.Const import FATAL_ERR, csLOCK_ON, DB_NOMAL_OK, DB_LOCK, NOMAL_OK, csGWSKBN_9, FILENM_SND, FILENM_TMP, \
    FTPFILE, FTPLOGFILE, FTPBATFILE, FTPFNDFILE, FTPENDFILE, FTPCMPMSG
from main.common.function.Common import TbCfsSysSELECT, dbField
from main.common.function import SqlExecute
from main.middleware.exception.exceptions import postgresException

dir_path = os.path.dirname(os.path.realpath(__file__))


def NacUniqGet(strUProGId, SystemData, strSelTbl, iniUpdCd, iniWsNo, strSelHozCd):
    try:
        intDataGet = 0
        for intCnt in range(11):
            tb_cfs_sys = TbCfsSysSELECT(SystemData, csLOCK_ON, iniUpdCd)
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
            sql = f"UPDATE TBCFSSYS{strSelTbl} "
            sql += f"SET IOJNONOW = {lngIoJNo},"
            sql += f"UNQFILENM = {dbField(strUnqFileNm)},"
            sql += f"UDATE = CURRENT_TIMESTAMP,"
            sql += f"UPROGID = {dbField(strUProGId)},"
            sql += f"UWSID = {dbField(iniWsNo)} "
            sql += f"WHERE HOZEICD = {dbField(strSelHozCd)}"
            SqlExecute(sql).execute()

        return NOMAL_OK, strIoJNo, strUnqFileNm
    except psycopg2.OperationalError as e:
        raise postgresException(Error=e, DbTbl="TBCFSSYS" + strSelTbl, SqlStr=sql)


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
        return NOMAL_OK, strNacHdr
    except:
        return FATAL_ERR, ""


def NacFtpPut(SystemData, strSndFilePath, strSndFileNm):
    strSndFile_Snd = strSndFileNm + FILENM_SND
    strSndFile_Tmp = strSndFileNm + FILENM_TMP
    try:
        if SystemData.GWSKBN == csGWSKBN_9:
            return NOMAL_OK
        for file in [FTPFILE, FTPLOGFILE, FTPBATFILE, FTPFNDFILE, FTPENDFILE]:
            if os.path.exists(file):
                os.remove(file)
        SetDataLength(os.path.join(strSndFilePath, "strSndFileNm"))
        strSndFileSnd = open(os.path.join(strSndFilePath, strSndFile_Snd), "w")
        strSndFileSnd.close()
        strSndFileTmp = open(os.path.join(strSndFilePath, strSndFile_Tmp), "w")
        strSndFileTmp.close()
        objFile = open(os.path.join(strSndFilePath, FTPFILE), "w")

        if SystemData.GWSKBN == 1:
            objFile.writelines(SystemData.GW1USERID)
            objFile.writelines(SystemData.GW1PASSWD)
            objFile.writelines("prompt")
            objFile.writelines("put " + strSndFile_Snd + " " + SystemData.GW1SDIR + strSndFile_Snd)
            objFile.writelines("put " + strSndFile_Tmp + " " + SystemData.GW1SDIR + strSndFile_Tmp)
        elif SystemData.GWSKBN == 2:
            objFile.writelines(SystemData.GW2USERID)
            objFile.writelines(SystemData.GW2PASSWD)
            objFile.writelines("prompt")
            objFile.writelines("put " + strSndFile_Snd + " " + SystemData.GW2SDIR + strSndFile_Snd)
            objFile.writelines("put " + strSndFile_Tmp + " " + SystemData.GW2SDIR + strSndFile_Tmp)
        else:
            return FATAL_ERR
        objFile.writelines("quit")
        objFile.close()
        objFile = open(os.path.join(strSndFilePath, FTPBATFILE), "w")
        objFile.writelines("echo " + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " > " + FTPLOGFILE)
        objFile.writelines("echo ------------------- >> " + FTPLOGFILE)
        if SystemData.GWSKBN == 1:
            objFile.writelines("ftp -s:" + FTPFILE + " " + SystemData.GW1IP + " >> " + FTPLOGFILE)
        elif SystemData.GWSKBN == 1:
            objFile.writelines("ftp -s:" + FTPFILE + " " + SystemData.GW2IP + " >> " + FTPLOGFILE)
        else:
            return FATAL_ERR
        objFile.writelines("echo ------------------- >> " + FTPLOGFILE)
        strCmpMsg = '"' + FTPCMPMSG + '"'
        objFile.writelines("find " + strCmpMsg + " < " + FTPLOGFILE + " > " + FTPFNDFILE)
        objFile.writelines("echo > " + FTPENDFILE)
        objFile.close()
        sngMaxTime = datetime.now() + timedelta(seconds=30)
        sngPauseTime = 0.5
        intCmpMsgCnt = 0
        sleep(1000)
        sngRetry = datetime.now()
        while sngMaxTime > datetime.now():
            if datetime.now() > sngRetry + timedelta(seconds=sngPauseTime):
                sngRetry = datetime.now()
                if os.path.exists(FTPENDFILE):
                    objFile = open(FTPENDFILE, "r")
                    objLineFile = objFile.readline()
                    while objLineFile:
                        if FTPCMPMSG == objLineFile:
                            intCmpMsgCnt = intCmpMsgCnt + 1
                        objLineFile = objFile.readline()
        if intCmpMsgCnt != 2:
            return FATAL_ERR
        return NOMAL_OK
    except:
        return FATAL_ERR
    finally:
        for file in [FTPFILE, FTPLOGFILE, FTPBATFILE, FTPFNDFILE, FTPENDFILE, strSndFile_Tmp]:
            if os.path.exists(file):
                os.remove(file)


def NacDataChange(strData, intDataLen):
    intLen = len(strData)
    nacDataChange = ""
    for intCnt in range(intDataLen):
        if intCnt <= intLen:
            if strData[intCnt] in ["\n", "\r"]:
                nacDataChange += " "
            else:
                nacDataChange += strData[intCnt]
        else:
            nacDataChange += " "


def SetDataLength(strFullPathFileName):
    ans = f"{os.path.getsize(strFullPathFileName): 06}"
    file = open(strFullPathFileName, "r").read()
    for i in range(6):
        strSetNum = int(ans[i]) + 48
        file = file[:393 + i] + strSetNum + file[393 + i:]
    open(strFullPathFileName, "w").write(file)
