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
