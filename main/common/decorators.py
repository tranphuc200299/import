import configparser
import os
import socket
from collections import defaultdict
from functools import wraps
from pathlib import Path
from main.common.function import Common


def update_context_fields():
    """
    Assign context data to request
    @update_context
    def my_view():
    ....
    """

    def inner_func(f):
        @wraps(f)
        def wrap(request, *args, **kwargs):
            request.context = defaultdict(str)
            if request.method == "POST":
                for field in request.POST:
                    request.context[field] = request.POST.get(field, "")
            return f(request, *args, **kwargs)

        return wrap

    return inner_func


def update_context():
    """
    Assign context data to request
    @update_context
    def my_view():
    ....
    """

    def inner_func(f):
        @wraps(f)
        def wrap(request, *args, **kwargs):
            request.context = defaultdict(str)
            if request.method == "POST":
                for field in request.POST:
                    request.context[field] = request.POST.get(field, "")
                return f(request, *args, **kwargs)
            return f(request, *args, **kwargs)

        return wrap

    return inner_func


def load_cfs_ini(cfs_menu):
    """
    Load Cfs ini
    @load_cfs_ini
    def my_view():
    ....
    """

    def inner_func(f):
        @wraps(f)
        def wrap(request, *args, **kwargs):
            request.cfs_ini = defaultdict(str)
            BASE_DIR = Path(__file__).resolve().parent.parent.parent
            config = configparser.ConfigParser()
            config.read(os.path.join(BASE_DIR, "config_ini", f"cfs_{cfs_menu}.ini"), encoding="SJIS")
            request.cfs_ini["iniWsNo"] = socket.gethostname()
            if config.has_section("CONFIG"):
                section_config = config["CONFIG"]
                if section_config.get("ID"):
                    request.cfs_ini["iniWsNo"] = cut_string(section_config["ID"])
                if section_config.get("WorkDir"):
                    request.cfs_ini["iniWsNo"] = cut_string(section_config["WorkDir"])
                if section_config.get("LocalDir"):
                    request.cfs_ini["iniLocalFile"] = cut_string(section_config["LocalDir"])
                if section_config.get("CrystalDir"):
                    request.cfs_ini["iniCrystalFile"] = cut_string(section_config["CrystalDir"])
                if section_config.get("SaveDir"):
                    request.cfs_ini["iniSaveFile"] = cut_string(section_config["SaveDir"])
                if section_config.get("KeepDays"):
                    request.cfs_ini["iniSaveDays"] = cut_string(section_config["KeepDays"])
                if section_config.get("StartTM"):
                    request.cfs_ini["iniStart"] = cut_string(section_config["StartTM"])
                if section_config.get("EndTM"):
                    request.cfs_ini["iniEnd"] = cut_string(section_config["EndTM"])
                if section_config.get("OraCont"):
                    request.cfs_ini["iniConDB"] = cut_string(section_config["OraCont"])
                if section_config.get("OraUser"):
                    request.cfs_ini["iniUid"] = cut_string(section_config["OraUser"])
                if section_config.get("OraPass"):
                    request.cfs_ini["iniPass"] = cut_string(section_config["OraPass"])
                if section_config.get("DIPri"):
                    iniDIPri = cut_string(section_config["DIPri"])
                    if iniDIPri == "PPR":
                        request.cfs_ini["iniDIPri"] = "0"
                    elif iniDIPri == "KSP":
                        request.cfs_ini["iniDIPri"] = "1"
            sections = [section for section in config.sections() if section.startswith("USER")]
            iniUpdNam = []
            iniUpdCd = []
            iniUpdTbl = []
            iniDispNam = []
            iniDispCd = []
            iniDispTbl = []
            for section in sections:
                user_section = config[section]
                iniUpdNam.append(cut_string(user_section["UpdName"]))
                iniUpdCd.append(cut_string(user_section["UpdCode"]))
                iniUpdTbl.append(cut_string(user_section["UpdTbl"]))
                iniDispNam.append(cut_string(user_section["DspName"]))
                iniDispCd.append(cut_string(user_section["DspCode"]))
                iniDispTbl.append(cut_string(user_section["DspTbl"]))
            if not Common.pfncDataSessionGet(request, "bond_area_name"):
                Common.pfncDataSessionSet(request, "bond_area_name", "K-DIC事務所")
            for index, value in enumerate(iniUpdNam):
                if value == Common.pfncDataSessionGet(request, "bond_area_name"):
                    index_bond_area = index
                    break
            request.cfs_ini["iniUpdNam"] = iniUpdNam[index_bond_area]
            request.cfs_ini["iniUpdCd"] = iniUpdCd[index_bond_area]
            request.cfs_ini["iniUpdTbl"] = iniUpdTbl[index_bond_area]
            request.cfs_ini["iniDispNam"] = iniDispNam[index_bond_area]
            request.cfs_ini["iniDispCd"] = iniDispCd[index_bond_area]
            request.cfs_ini["iniDispTbl"] = iniDispTbl[index_bond_area]
            return f(request, *args, **kwargs)

        def cut_string(string: str):
            strings = string.split("/*")
            output = strings[0].strip()
            return output

        return wrap

    return inner_func
