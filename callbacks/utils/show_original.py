import json
import os

import discord

from modules.localization import Localization


async def show_original_callback(interaction: discord.Interaction):
    index, inference_id, _ = interaction.custom_id.split("-")
    index = int(index)

    with open(os.path.join("data", "history", f"{inference_id}.json")) as io_stream:
        request_json = json.load(io_stream)
    request_data = request_json['data']
    request_author = request_json['author']

    await interaction.response.send_message(
        content=f"**{request_data['prompt']}** - {Localization(str()).get_localization('bot')['messages']['original'].format(index + 1, request_author['name'], interaction.user.mention)}",
        file=discord.File(os.path.join("cache", "txt2img", inference_id, f"image_{index}.png")), ephemeral=True)
