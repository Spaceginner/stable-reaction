import json
import os

import discord

from modules.localization import Localization


# TODO make compatible with upscale
async def show_info_callback(interaction: discord.Interaction):
    request_type_str, inference_id, _ = interaction.custom_id.split("-")

    with open(os.path.join("data", "history", f"{inference_id}.json")) as io_stream:
        request_json = json.load(io_stream)
        request_data = request_json["data"]
        request_author = request_json["author"]
    await interaction.response.send_message(ephemeral=True, content=f"""\
{Localization(str()).get_localization('bot')['messages']['info'].format(request_type_str, inference_id)}:
```
author_name: {request_author['name']}
author_id: {request_author['id']}
---
prompt: {request_data['prompt']}
neg_prompt: {request_data['negative_prompt']}
res_x: {request_data['width']}
res_y: {request_data['height']}
cfg_scale: {request_data['cfg_scale']}
sampler: {request_data['sampler_name']}
steps: {request_data['steps']}
seed: {request_data['seed']}
count: {request_data['batch_size']}
```\
""")
