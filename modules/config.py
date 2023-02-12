import json
import os
import sys

import requests
import yaml

from modules import singleton
from modules.api.inference import API


class Config(metaclass=singleton.SingletonMetaclass):
    _general = None
    _bot = None
    _inference = None
    _environment = None
    _remote = None
    _values = None

    def __init__(self, config_path: str, environment_path: str):
        try:
            with open(config_path) as io_stream:
                config_buffer = yaml.safe_load(io_stream)

            self._general = config_buffer['general']
            self._bot = config_buffer['bot']
            self._inference = config_buffer['inference']
            self._values = config_buffer['values']

            if os.path.isfile(environment_path):
                with open(environment_path) as io_stream:
                    self._environment = json.load(io_stream)

            if self._inference["url"][-1] == "/":
                self._inference["url"] = self._inference["url"][:-1]
        except Exception as e:
            print(e)
            input("Press ENTER to continue...")

    def init_remote(self, api: API):
        try:
            self._remote = {
                'samplers': api.samplers(),
                'upscalers': api.upscalers(),
                'models': api.models(),
                'embeddings': {
                    "loaded": api.embeddings(True),
                    "skipped": api.embeddings(False)
                },
                'hypernetworks': api.hypernetworks(),
                'styles': api.styles()
            }
        except requests.exceptions.ConnectionError as e:
            input(f"""
{e}

Running installation of AUTOMATIC1111 WebUI is not found
Check following things:
    WebUI runs with `--api` flag
    URL to the WebUI in the config file is correct

Press ENTER to exit...\
            """)
            sys.exit(1)

    def get_general(self):
        return self._general

    def get_bot(self):
        return self._bot

    def get_inference(self):
        return self._inference

    def get_environment(self):
        return self._environment

    def get_remote(self):
        return self._remote

    def get_values(self, key):
        return self._values[key]
