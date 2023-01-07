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

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"[BOND_AREA_NAME_ERROR]: {self.message}"
