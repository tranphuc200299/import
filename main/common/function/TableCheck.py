import logging

from main.common.function import SqlExecute, Common
from django.db import IntegrityError
from main.common.function.Const import DB_NOT_FIND, DB_NOMAL_OK, DB_FATAL_ERR

_logger = logging.getLogger(__name__)


def TbVessel_TableCheck(strOpeCd, strSelTbl):
    try:
        sql = "SELECT COUNT(OPECD) AS DCNT "
        sql += f"FROM TBOPE{strSelTbl} "
        sql += f"WHERE VESSELCD = {Common.dbField(strOpeCd)}"
        RsTbVessel = SqlExecute(sql).all()
        if RsTbVessel.Rows[0]["DCNT"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except IntegrityError as ie:
        _logger.error(ie)
        return DB_FATAL_ERR


def TbOpe_TableCheck(strOpeCd, strSelTbl):
    try:
        sql = "SELECT COUNT(OPECD) AS DCNT "
        sql += f"FROM TBOPE{strSelTbl} "
        sql += f"WHERE OPECD = {Common.dbField(strOpeCd)}"
        RsTbOpe = SqlExecute(sql).all()
        if RsTbOpe.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except IntegrityError as ie:
        _logger.error(ie)
        return DB_FATAL_ERR


def TbPort_TableCheck(strOpeCd, strSelTbl):
    try:
        sql = "SELECT COUNT(PORTCD) AS DCNT "
        sql += f"FROM TBPORT{strSelTbl} "
        sql += f"WHERE PORTCD = {Common.dbField(strOpeCd)}"
        RsTbPort = SqlExecute(sql).all()
        if RsTbPort.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except IntegrityError as ie:
        _logger.error(ie)
        return DB_FATAL_ERR


def TbPackg_TableCheck(strOpeCd, strSelTbl):
    try:
        sql = "SELECT COUNT(PACKCD) AS DCNT "
        sql += f"FROM TBPACKG{strSelTbl} "
        sql += f"WHERE PACKCD = {Common.dbField(strOpeCd)}"
        RsTbPackg = SqlExecute(sql).all()
        if RsTbPackg.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except IntegrityError as ie:
        _logger.error(ie)
        return DB_FATAL_ERR


def TbSTani_TableCheck(strOpeCd, strSyubtKbn, strSelTbl):
    try:
        sql = "SELECT COUNT(STANICD) AS DCNT "
        sql += f"FROM TBSTANI{strSelTbl} "
        sql += f"WHERE STANICD = {Common.dbField(strOpeCd)}"
        sql += f" AND SYUBTKBN = {Common.dbField(strSyubtKbn)}"
        RsTbSTani = SqlExecute(sql).all()
        if RsTbSTani.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except IntegrityError as ie:
        _logger.error(ie)
        return DB_FATAL_ERR


def TbZWork_TableCheck(strZWorkCd, strSelTbl):
    try:
        sql = "SELECT COUNT(ZWORKCD) AS DCNT "
        sql += f"FROM TBZWORK{strSelTbl} "
        sql += f"WHERE ZWORKCD = {Common.dbField(strZWorkCd)}"
        RsTbZWork = SqlExecute(sql).all()
        if RsTbZWork.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except IntegrityError as ie:
        _logger.error(ie)
        return DB_FATAL_ERR


def TbForward_TableCheck(strFwdCd, strSelTbl):
    try:
        sql = "SELECT COUNT(FWDCD) AS DCNT "
        sql += f"FROM TBFORWARD{strSelTbl} "
        sql += f"WHERE FWDCD = {Common.dbField(strFwdCd)}"
        RsTbForward = SqlExecute(sql).all()
        if RsTbForward.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except IntegrityError as ie:
        _logger.error(ie)
        return DB_FATAL_ERR


def TbInland_TableCheck(strInlandCd, strSelTbl):
    try:
        sql = "SELECT COUNT(INLANDCD) AS DCNT "
        sql += f"FROM TBINLAND{strSelTbl} "
        sql += f"WHERE INLANDCD = {Common.dbField(strInlandCd)}"
        RsTbInland = SqlExecute(sql).all()
        if RsTbInland.Rows[0]["dcnt"] == 0:
            return DB_NOT_FIND
        else:
            return DB_NOMAL_OK
    except IntegrityError as ie:
        _logger.error(ie)
        return DB_FATAL_ERR
