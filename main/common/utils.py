import configparser
import json
import os
import socket
from collections import OrderedDict
from pathlib import Path

from django.http import JsonResponse

from importCFS.settings import env_config
from main.common.function import Common
from main.middleware.exception.exceptions import RuntimeException, BondAreaNameException
from main.middleware.exception.message import E00002


class Response(object):
    def __init__(self, request):
        self.request = request

    def json_response_event_js_html(self, id_show_data) -> JsonResponse:
        if type(id_show_data) is list:
            data = {
                "gSetField": self.request.context["gSetField"],
            }
            for show_data in id_show_data:
                data[show_data] = self.request.context[show_data]
        else:
            data = {
                id_show_data: self.request.context[id_show_data],
                "gSetField": self.request.context["gSetField"],
            }
        return JsonResponse(data)


class ConfigIni(object):

    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.config_ini_dir = os.path.join(base_dir, "config_ini")

    def get_config_ini_info(self, request, cfs_menu):
        if cfs_menu:
            config = configparser.ConfigParser()
            config.read(os.path.join(self.config_ini_dir, f"cfs_{cfs_menu}.ini"), encoding="utf-8")
            request.cfs_ini["iniWsNo"] = socket.gethostname()[:10]
            if config.has_section("CONFIG"):
                section_config = config["CONFIG"]
                if section_config.get("ID"):
                    request.cfs_ini["iniWsNo"] = self.__cut_string(section_config["ID"])
                if section_config.get("WorkDir"):
                    request.cfs_ini["iniWorkFile"] = self.__cut_string(section_config["WorkDir"])
                if section_config.get("LocalDir"):
                    request.cfs_ini["iniLocalFile"] = self.__cut_string(section_config["LocalDir"])
                if section_config.get("CrystalDir"):
                    request.cfs_ini["iniCrystalFile"] = self.__cut_string(section_config["CrystalDir"])
                if section_config.get("SaveDir"):
                    request.cfs_ini["iniSaveFile"] = self.__cut_string(section_config["SaveDir"])
                if section_config.get("KeepDays"):
                    request.cfs_ini["iniSaveDays"] = self.__cut_string(section_config["KeepDays"])
                if section_config.get("StartTM"):
                    request.cfs_ini["iniStart"] = self.__cut_string(section_config["StartTM"])
                if section_config.get("EndTM"):
                    request.cfs_ini["iniEnd"] = self.__cut_string(section_config["EndTM"])
                if section_config.get("OraCont"):
                    request.cfs_ini["iniConDB"] = self.__cut_string(section_config["OraCont"])
                if section_config.get("OraUser"):
                    request.cfs_ini["iniUid"] = self.__cut_string(section_config["OraUser"])
                if section_config.get("OraPass"):
                    request.cfs_ini["iniPass"] = self.__cut_string(section_config["OraPass"])
                if section_config.get("DIPri"):
                    iniDIPri = self.__cut_string(section_config["DIPri"])
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
                iniUpdNam.append(self.__cut_string(user_section["UpdName"]))
                iniUpdCd.append(self.__cut_string(user_section["UpdCode"]))
                iniUpdTbl.append(self.__cut_string(user_section["UpdTbl"]))
                iniDispNam.append(self.__cut_string(user_section["DspName"]))
                iniDispCd.append(self.__cut_string(user_section["DspCode"]))
                iniDispTbl.append(self.__cut_string(user_section["DspTbl"]))
            index_bond_area = None
            for index, value in enumerate(iniUpdNam):
                if value == Common.pfncDataSessionGet(request, "bond_area_name"):
                    index_bond_area = index
                    break
            if index_bond_area is not None:
                request.cfs_ini["iniUpdNam"] = iniUpdNam[index_bond_area]
                request.cfs_ini["iniUpdCd"] = iniUpdCd[index_bond_area]
                request.cfs_ini["iniUpdTbl"] = iniUpdTbl[index_bond_area]
                request.cfs_ini["iniDispNam"] = iniDispNam[index_bond_area]
                request.cfs_ini["iniDispCd"] = iniDispCd[index_bond_area]
                request.cfs_ini["iniDispTbl"] = iniDispTbl[index_bond_area]
            if request.resolver_match.url_name == 'f_cfsc2900':
                request.context["calendar"] = []
                arr = []
                for i in range(42):
                    arr.append(i)
                    if (i + 1) % 7 == 0:
                        request.context["calendar"].append(arr)
                        arr = []
        bond_area_name_select = request.GET.get('bond_area_name_select', None)
        if bond_area_name_select is None:
            bond_area_name_select = Common.pfncDataSessionGet(request, "bond_area_name")
        Common.pfncDataSessionSet(request, "bond_area_name", bond_area_name_select)
        if not Common.pfncDataSessionGet(request, "bond_area_name"):
            Common.pfncDataSessionSet(request, "bond_area_name", self.get_default_area_name())
        list_menu = self.get_list_menu_by_area_name(Common.pfncDataSessionGet(request, "bond_area_name"))
        request.context["sider_bar"] = FileDirUtil.get_sider_bar_by_menu_list(list_menu)
        url_name = request.resolver_match.url_name
        if url_name != "home":
            request.context["breadcumbs"] = FileDirUtil.get_breadcumbs_by_path_name(request.resolver_match.url_name)
        if cfs_menu not in list_menu:
            raise BondAreaNameException(Common.pfncDataSessionGet(request, "bond_area_name"))

    def get_default_area_name(self):
        name = env_config("DEFAULT_BOND_AREA_NAME")
        if name is None:
            raise RuntimeException(error_code=E00002, message="Missing configuration DEFAULT_BOND_AREA_NAME")
        if name not in self.get_all_area_name():
            raise RuntimeException(error_code=E00002,
                                   message="Default bond area name does not exists in config ini file")
        return env_config("DEFAULT_BOND_AREA_NAME")

    def get_all_area_name(self):
        config = configparser.ConfigParser()
        file_names = os.listdir(self.config_ini_dir)
        names = list()
        for filename in file_names:
            config.read(os.path.join(self.config_ini_dir, filename), encoding="utf-8")
            sections = [section for section in config.sections() if section.startswith("USER")]
            for section in sections:
                user_section = config[section]
                if self.__cut_string(user_section["DspName"]) not in names:
                    names.append(self.__cut_string(user_section["DspName"]))
        names.sort()
        return names

    def get_list_menu_by_area_name(self, area_name):
        file_names = os.listdir(self.config_ini_dir)
        dict_menu_area = dict()
        for filename in file_names:
            config = configparser.ConfigParser()
            config.read(os.path.join(self.config_ini_dir, filename), encoding="utf-8")
            sections = [section for section in config.sections() if section.startswith("USER")]
            names = list()
            for section in sections:
                user_section = config[section]
                names.append(self.__cut_string(user_section["DspName"]))
            key = filename[filename.index("_") + 1:filename.index(".")]
            dict_menu_area[key] = names
        list_menu_output = [k for k, v in dict_menu_area.items() if area_name in v]
        return list_menu_output + [""]

    def __cut_string(self, string: str):
        strings = string.split("/*")
        output = strings[0].strip()
        return output


class FileDirUtil:

    @staticmethod
    def get_html_dir_by_url_name(url_name):
        base_dir = Path(__file__).resolve().parent.parent
        html_dir = os.path.join(base_dir, "templates", "menu")
        menu_folders = os.listdir(html_dir)
        for menu_folder in menu_folders:
            menu_files = os.listdir(os.path.join(base_dir, "templates", "menu", menu_folder))
            if f"{url_name}.html" in menu_files:
                return f"menu/{menu_folder}/{url_name}.html"
        return "home.html"

    @staticmethod
    def get_sider_bar_by_menu_list(menu_list):
        new_menu_list = menu_list.copy()
        new_menu_list.remove('')
        new_menu_list.sort()
        base_dir = Path(__file__).resolve().parent.parent.parent
        sider_bar_dir = os.path.join(base_dir, "config_sider_bar", "sider_bar.json")
        menu_output = OrderedDict()
        with open(sider_bar_dir, encoding="utf-8") as json_file:
            data = json.load(json_file)
            for menu in new_menu_list:
                get_menu = data.get(menu, None)
                if get_menu is None:
                    raise RuntimeException(error_code=E00002, message="Has an error when generate menu")
                menu_output[menu] = data[menu]
        return menu_output

    @staticmethod
    def get_breadcumbs_by_path_name(url_name):
        base_dir = Path(__file__).resolve().parent.parent.parent
        sider_bar_dir = os.path.join(base_dir, "config_sider_bar", "sider_bar.json")
        with open(sider_bar_dir, encoding="utf-8") as json_file:
            data = json.load(json_file)
            output = []
            for k, v in data.items():
                dict_home = {'url': 'home', 'title': 'ホーム'}
                dict_ = {'url': '#', 'title': v['title']}
                sub_menu = v['sub_menu']
                for s in sub_menu:
                    output.append(dict_home)
                    output.append(dict_)
                    output, is_find = FileDirUtil.recursive(s, url_name, output)
                    if is_find:
                        return output

    @staticmethod
    def recursive(jsons, url_name, output):
        if jsons is None:
            output.clear()
            return output, False
        screen_url = jsons['url']
        screen_title = jsons['title']
        dict_ = {'url': screen_url, 'title': screen_title}
        output.append(dict_)
        if url_name == screen_url:
            return output, True
        return FileDirUtil.recursive(jsons.get('sub_menu', None), url_name, output)
