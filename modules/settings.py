import json
import os
from threading import Lock

from modules.config import Config
from modules.singleton import SingletonMetaclass


class Settings(metaclass=SingletonMetaclass):
    def __init__(self, settings_path: str):
        self._settings_path = settings_path
        os.makedirs(self._settings_path, exist_ok=True)

        self._cache = {}
        self._lock = Lock()

    def get_user(self, user_id: str):
        if user_id not in self._cache.keys():
            self._load_data(user_id)

        return self._cache[user_id]

    def set_user(self, user_id: str, command: str, option: str, value):
        if not os.path.isfile(os.path.join(self._settings_path, f'{user_id}.json')):
            self._create_default(user_id)
        else:
            self._validate_settings(user_id)

        with self._lock:
            self._invalidate_cache(user_id)

            with open(os.path.join(self._settings_path, f'{user_id}.json')) as io_stream:
                user_settings = json.load(io_stream)

            user_settings[command][option] = value

            with open(os.path.join(self._settings_path, f'{user_id}.json'), 'w') as io_stream:
                json.dump(user_settings, io_stream)

    def _load_data(self, user_id: str):
        if not os.path.isfile(os.path.join(self._settings_path, f'{user_id}.json')):
            self._create_default(user_id)
        else:
            self._validate_settings(user_id)

        with open(os.path.join(self._settings_path, f'{user_id}.json')) as io_stream:
            self._cache[user_id] = json.load(io_stream)

    def _create_default(self, user_id: str):
        default_config = Config(str(), str()).get_values('defaults')

        with open(os.path.join(self._settings_path, f'{user_id}.json'), 'w') as io_stream:
            json.dump(default_config, io_stream)

    def _invalidate_cache(self, user_id: str):
        if user_id in self._cache.keys():
            self._cache.pop(user_id)

    def _validate_settings(self, user_id: str):
        with self._lock:
            self._invalidate_cache(user_id)

            default_config: dict[dict] = Config(str(), str()).get_values('defaults')

            with open(os.path.join(self._settings_path, f'{user_id}.json')) as io_stream:
                user_settings: dict[dict] = json.load(io_stream)

            # recursively searches with the depth of 2
            missing_keys = [k for k in default_config.keys() if k not in user_settings.keys()]
            for missing_key in missing_keys:
                user_settings[missing_key] = default_config[missing_key]
            for command_key in user_settings.keys():
                missing_subkeys = [k for k in default_config[command_key].keys() if k not in user_settings[command_key].keys()]

                for missing_subkey in missing_subkeys:
                    user_settings[command_key][missing_subkey] = default_config[command_key][missing_subkey]

            with open(os.path.join(self._settings_path, f'{user_id}.json'), 'w') as io_stream:
                json.dump(user_settings, io_stream)
