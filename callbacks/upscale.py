import asyncio
import json
import os

import discord

from callbacks.interrupt import interrupt_callback
from callbacks.restore import restore_callback
from modules.api import request_types, queue
from modules.localization import Localization
from modules.settings import Settings


async def upscale_callback(interaction: discord.Interaction):
    inference_queue = queue.Queue(int(), int())

    index, inference_id, _ = interaction.custom_id.split("-")
    index = int(index)

    with open(os.path.join("data", "history", f"{inference_id}.json")) as io_stream:
        origin_request_data = json.load(io_stream)['data']

    await interaction.response.send_message(
        content=f"{Localization(str()).get_localization('bot')['messages']['upscaling'].format(index + 1, origin_request_data['prompt'], interaction.user.mention)} ({Localization(str()).get_localization('bot')['messages']['queue_wait']}...)")

    response_msg = await interaction.original_response()

    user_settings = Settings(str()).get_user(str(interaction.user.id))['upscale']
    request = request_types.Upscale(index, user_settings['factor'], user_settings['upscaler'], response_msg.id, inference_id, interaction.user.id,
                                    interaction.user.name, 3)
    inference_queue.put(request)

    interrupt_button = discord.ui.Button(label=Localization(str()).get_localization("bot")['messages']['cancel'], custom_id=f"{inference_id}-upscale-{interaction.user.id}",
                                         style=discord.ButtonStyle.danger)
    interrupt_button.callback = interrupt_callback

    while not request.status.get()["is_processing"] and not request.status.get()["is_interrupted"]:
        place = request.status.get()["place"]
        await response_msg.edit(
            content=f"{Localization(str()).get_localization('bot')['messages']['upscaling'].format(index + 1, origin_request_data['prompt'], interaction.user.mention)} ({Localization(str()).get_localization('bot')['messages']['queue_wait']}{f': {place}' if place else '...'})",
            view=discord.ui.View(interrupt_button, timeout=None))
        await asyncio.sleep(0.075)

    await response_msg.edit(
        content=f"{Localization(str()).get_localization('bot')['messages']['upscaling'].format(index + 1, origin_request_data['prompt'], interaction.user.mention)} ({Localization(str()).get_localization('bot')['messages']['process_wait']}...)")
    while not request.status.get()["is_finished"] and not request.status.get()["is_interrupted"]:
        await asyncio.sleep(0.15)

    if request.status.get()["is_interrupted"]:
        cancelled_view_items = []

        restore_button = discord.ui.Button(label='Restore', custom_id=f'{response_msg.id}-restore')
        restore_button.callback = restore_callback

        cancelled_view_items.append(restore_button)

        await response_msg.edit(
            f"{Localization(str()).get_localization('bot')['messages']['upscaling'].format(index + 1, origin_request_data['prompt'], interaction.user.mention)} ({Localization(str()).get_localization('bot')['messages']['cancelled']})",
            view=discord.ui.View(*cancelled_view_items))
        return

    await response_msg.edit(
        content=f"**{origin_request_data['prompt']}** - {Localization(str()).get_localization('bot')['messages']['upscaled'].format(interaction.user.mention)} ({round(request.get_waiting_time(), 2)} + {round(request.get_processing_time(), 2)} {Localization(str()).get_localization('bot')['messages']['seconds']})",
        file=discord.File(os.path.join("cache", "upscale", str(response_msg.id), f"image_{index}.jpg")), view=None)
