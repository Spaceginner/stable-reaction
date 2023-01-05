import json
import os.path


cache = {}


async def create_global_settings(user_id: int, default_settings: dict):
    with open(os.path.join("settings", str(user_id), "global.json"), "w") as io_stream:
        json.dump(default_settings, io_stream)


async def create_local_settings(user_id: int, guild_id: int):
    with open(os.path.join("settings", str(user_id), "global.json"), "r") as io_stream:
        default_settings = json.load(io_stream)

    with open(os.path.join("settings", str(user_id), f"{guild_id}.json"), "w") as io_stream:
        json.dump(default_settings, io_stream)


async def prepare_settings(user_id: int, guild_id: int, default_settings: dict):
    if not os.path.isdir(os.path.join("settings", str(user_id))):
        os.makedirs(os.path.join("settings", str(user_id)), exist_ok=True)

    if not os.path.isfile(os.path.join("settings", str(user_id), "global.json")):
        await create_global_settings(user_id, default_settings)

    if not os.path.isfile(os.path.join("settings", str(user_id), f"{guild_id}.json")):
        await create_local_settings(user_id, guild_id)


async def load_settings(user_id: int, guild_id: int, item: str):
    global cache

    if not cache[str(user_id)][str(guild_id)]:
        with open(os.path.join("settings", str(user_id), f"{guild_id}.json"), "r") as io_stream:
            cache[str(user_id)][str(guild_id)] = json.load(io_stream)

    return cache[str(user_id)][str(guild_id)][item]


def invalidate_cache(user_id: int, guild_id: int):
    global cache

    cache[str(user_id)][str(guild_id)] = None
