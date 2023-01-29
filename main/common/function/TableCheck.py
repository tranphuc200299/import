import logging
import psycopg2
from main.common.function import SqlExecute, Common
from main.common.function.Const import DB_NOT_FIND, DB_NOMAL_OK
from main.middleware.exception.exceptions import PostgresException

_logger = logging.getLogger(__name__)


def TbVessel_TableCheck(strVesselCd, strSelTbl):
    sql = ""
    try:
        sql += "SELECT COUNT(VESSELCD) AS dcnt "
        sql += f"FROM TBVESSEL{strSelTbl} "
        sql += f"WHERE VESSELCD = {Common.dbField(strVesselCd)}"
        RsTbVessel = SqlExecute(sql).all()
        if RsTbVessel.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except psycopg2.OperationalError as e:
        _logger.error(e)
        raise PostgresException(Error=e, DbTbl="TBVESSEL" + strSelTbl, SqlStr=sql)


def TbOpe_TableCheck(strOpeCd, strSelTbl):
    sql = ""
    try:
        sql += "SELECT COUNT(OPECD) AS dcnt "
        sql += f"FROM TBOPE{strSelTbl} "
        sql += f"WHERE OPECD = {Common.dbField(strOpeCd)}"
        RsTbOpe = SqlExecute(sql).all()
        if RsTbOpe.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except psycopg2.OperationalError as e:
        raise PostgresException(Error=e, DbTbl="TBOPE" + strSelTbl, SqlStr=sql)


def TbPort_TableCheck(strPortCd, strSelTbl):
    sql = ""
    try:
        sql = "SELECT COUNT(PORTCD) AS dcnt "
        sql += f"FROM TBPORT{strSelTbl} "
        sql += f"WHERE PORTCD = {Common.dbField(strPortCd)}"
        RsTbPort = SqlExecute(sql).all()
        if RsTbPort.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except psycopg2.OperationalError as e:
        _logger.error(e)
        raise PostgresException(Error=e, DbTbl="TBPORT" + strSelTbl, SqlStr=sql)


def TbPackg_TableCheck(strPackCd, strSelTbl):
    sql = ""
    try:
        sql = "SELECT COUNT(PACKCD) AS dcnt "
        sql += f"FROM TBPACKG{strSelTbl} "
        sql += f"WHERE PACKCD = {Common.dbField(strPackCd)}"
        RsTbPackg = SqlExecute(sql).all()
        if RsTbPackg.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except psycopg2.OperationalError as e:
        _logger.error(e)
        raise PostgresException(Error=e, DbTbl="TBPACKG" + strSelTbl, SqlStr=sql)


def TbSTani_TableCheck(strSTaniCd, strSyubtKbn, strSelTbl):
    sql = ""
    try:
        sql = "SELECT COUNT(STANICD) AS dcnt "
        sql += f"FROM TBSTANI{strSelTbl} "
        sql += f"WHERE STANICD = {Common.dbField(strSTaniCd)}"
        sql += f" AND SYUBTKBN = {Common.dbField(strSyubtKbn)}"
        RsTbSTani = SqlExecute(sql).all()
        if RsTbSTani.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except psycopg2.OperationalError as e:
        _logger.error(e)
        raise PostgresException(Error=e, DbTbl="TBSTANI" + strSelTbl, SqlStr=sql)


def TbZWork_TableCheck(strZWorkCd, strSelTbl):
    sql = ""
    try:
        sql = "SELECT COUNT(ZWORKCD) AS dcnt "
        sql += f"FROM TBZWORK{strSelTbl} "
        sql += f"WHERE ZWORKCD = {Common.dbField(strZWorkCd)}"
        RsTbZWork = SqlExecute(sql).all()
        if RsTbZWork.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except psycopg2.OperationalError as e:
        _logger.error(e)
        raise PostgresException(Error=e, DbTbl="TBZWORK" + strSelTbl, SqlStr=sql)


def TbForward_TableCheck(strFwdCd, strSelTbl):
    sql = ""
    try:
        sql = "SELECT COUNT(FWDCD) AS dcnt "
        sql += f"FROM TBFORWARD{strSelTbl} "
        sql += f"WHERE FWDCD = {Common.dbField(strFwdCd)}"
        RsTbForward = SqlExecute(sql).all()
        if RsTbForward.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except psycopg2.OperationalError as e:
        _logger.error(e)
        raise PostgresException(Error=e, DbTbl="TBFORWARD" + strSelTbl, SqlStr=sql)


def TbInland_TableCheck(strInlandCd, strSelTbl):
    sql = ""
    try:
        sql = "SELECT COUNT(INLANDCD) AS dcnt "
        sql += f"FROM TBINLAND{strSelTbl} "
        sql += f"WHERE INLANDCD = {Common.dbField(strInlandCd)}"
        RsTbInland = SqlExecute(sql).all()
        if RsTbInland.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except psycopg2.OperationalError as e:
        _logger.error(e)
        raise PostgresException(Error=e, DbTbl="TBINLAND" + strSelTbl, SqlStr=sql)
