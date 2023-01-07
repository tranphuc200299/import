from main.common.function.Const import FATAL_ERR, csLOCK_ON, DB_NOMAL_OK, DB_LOCK
from main.common.function.Common import TbCfsSysSELECT
from time import sleep
def NacUniqGet(strUProGId , SystemData, strUnqFileNm, strIoJNo, iniUpdCd, iniUpdTbl):
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
        strNowDate = Format(CDate(Now), "YYYYMMDDHHMMSS")



    except:
        #OraErrorH "TBCFSSYS" & strSelTbl, sql
        return FATAL_ERR