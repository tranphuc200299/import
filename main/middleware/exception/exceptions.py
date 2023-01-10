from main.middleware.exception.message import CUSTOM_EXCEPTION


class RuntimeException(Exception):

    def __init__(self, *args, **kwargs):
        self.error_code = kwargs.pop('error_code', '')
        self.values = kwargs

    def get_message(self):
        message = CUSTOM_EXCEPTION.get(self.error_code, '')
        for key, value in self.values.items():
            message = message.replace("{" + str(key) + "}", value)
        return message

    def __str__(self):
        return f'ERROR_CODE = {self.error_code}, MESSAGE = {self.get_message()}'


class BondAreaNameException(Exception):

    def __init__(self, bond_area_name):
        self.bond_area_name = bond_area_name

    def __str__(self):
        return f"Request screen doesn't exists in bond area name: {format(self.bond_area_name)}"


class postgresException(Exception):
    def __init__(self, *args, **kwargs):
        self.DbTbl = kwargs.pop('DbTbl', '')
        self.SqlStr = kwargs.pop('SqlStr', '')
        self.Error = kwargs.pop('Error ', '')

    def get_message(self):
        if self.Error.pgcode == "55P03":
            message = "ＤＢ読み込みエラー発生\n\n該当データは他で使用中です。"
        else:
            message = "ＤＢエラー発生\n\n" + str(self.Error) + "\n" + self.SqlStr
        return message

    def __str__(self):
        return f'ERROR_CODE = {self.Error.pgcode}, MESSAGE = {self.get_message()}'
