import json
import os.path

from modules import singleton


class Localization(metaclass=singleton.SingletonMetaclass):
    def __init__(self, locale):
        self._locale = locale

        with open(os.path.join("resources", "localizations", f"{locale}.json")) as io_stream:
            self._localization = json.load(io_stream)

    def get_locale(self):
        return self._locale

    def get_localization(self, key: str):
        return self._localization[key]
