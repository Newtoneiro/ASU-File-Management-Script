import os
import json

CONFIG_FILE = 'config.json'
RWX_TO_NUMBER = {'r': 4, 'w': 2, 'x': 1, '-': 0}
dirname = os.path.dirname(__file__)
config_path = os.path.join(dirname, CONFIG_FILE)


class Config:
    """
    Class responsible for config management
    """
    def __init__(self, filename: str = config_path):
        self._filename = filename
        self._json = self.get_json_content()

    def get_json_content(self) -> dict:
        with open(self._filename) as file:
            return json.load(file)

    def get_oct_permissions(self, permissions: str) -> int:
        if len(permissions) != 9:
            raise ValueError(
                f"{permissions} is not a valid permission string.")
        result = ""
        for i in range(0, 9, 3):
            partition = 0
            for perm_bit in permissions[i:i+3]:
                partition += RWX_TO_NUMBER[perm_bit]
            result += str(partition)
        return int(result)

    def __getattr__(self, __name: str) -> str or list[str]:
        if __name in self._json.keys():
            return self._json[__name]
        raise AttributeError(
            f"{self.__class__.__name__} nie ma atrybutu {__name}."
        )
