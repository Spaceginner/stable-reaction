import asyncio
import json
import os

import discord

from callbacks.interrupt import interrupt_callback
from callbacks.restore import restore_callback
from callbacks.upscale import upscale_callback
from callbacks.utils.show_info import show_info_callback
from callbacks.utils.show_original import show_original_callback
from modules.api import request_types, inference, queue
from modules.localization import Localization


async def regenerate_callback(interaction: discord.Interaction):
    api = inference.API(str())
    inference_queue = queue.Queue(int(), int())

    inference_id, _ = interaction.custom_id.split("-")

    request_data = json.load(open(os.path.join("data", "history", f"{inference_id}.json")))["data"]

    await interaction.response.send_message(content=f"**{request_data['prompt']}** - {interaction.user.mention} ({Localization(str()).get_localization('bot')['messages']['queue_wait']}...)")

    response_msg = await interaction.original_response()
    response_msg_id = response_msg.id

    request = request_types.Text2Img(request_data["prompt"], request_data["negative_prompt"], request_data["steps"],
                                     request_data["batch_size"], -1, request_data["cfg_scale"],
                                     request_data["width"], request_data["height"], request_data["sampler_name"],
                                     response_msg_id, interaction.user.id, interaction.user.name, 1)
    inference_queue.put(request)

    interrupt_button = discord.ui.Button(label=Localization(str()).get_localization("bot")['messages']['cancel'],
                                         custom_id=f"{response_msg_id}-txt2img-{interaction.user.id}",
                                         style=discord.ButtonStyle.danger)
    interrupt_button.callback = interrupt_callback

    while not request.status.get()["is_processing"] and not request.status.get()["is_interrupted"]:
        place = request.status.get()["place"]
        await response_msg.edit(
            content=f"**{request_data['prompt']}** - {interaction.user.mention} ({Localization(str()).get_localization('bot')['messages']['queue_wait']}{f': {place}' if place else '...'})",
            view=discord.ui.View(interrupt_button, timeout=None))
        await asyncio.sleep(0.075)

    while not request.status.get()["is_finished"] and not request.status.get()["is_interrupted"]:
        request.progress.set_progress(await api.progress())
        await response_msg.edit(
            content=f"**{request_data['prompt']}** - {interaction.user.mention} ({request.progress})")
        await asyncio.sleep(0.075)

    if request.status.get()["is_interrupted"]:
        cancelled_view_items = []

        restore_button = discord.ui.Button(label='Restore', custom_id=f'{response_msg_id}-restore')
        restore_button.callback = restore_callback

        cancelled_view_items.append(restore_button)

        await response_msg.edit(f"**{request_data['prompt']}** - {interaction.user.mention} ({Localization(str()).get_localization('bot')['messages']['cancelled']})", view=discord.ui.View(*cancelled_view_items))
        return

    done_view_items = []

    # Upscale button
    for index in range(request_data['batch_size']):
        button = discord.ui.Button(label=f"U{index + 1}", row=0,
                                   custom_id=f"{index}-{response_msg_id}-upscale")
        button.callback = upscale_callback

        done_view_items.append(button)

    # Show original button
    for index in range(request_data['batch_size']):
        button = discord.ui.Button(label=f"S{index + 1}", row=1,
                                   custom_id=f"{index}-{response_msg_id}-original")
        button.callback = show_original_callback

        done_view_items.append(button)

    # Regenerate button
    button = discord.ui.Button(label="Regen", row=0,
                               custom_id=f"{response_msg_id}-regen")
    button.callback = regenerate_callback
    done_view_items.append(button)

    # Info button
    button = discord.ui.Button(label="Info", row=1, custom_id=f"txt2img-{response_msg_id}-info")
    button.callback = show_info_callback
    done_view_items.append(button)

    done_view = discord.ui.View(*done_view_items, timeout=None)

    await response_msg.edit(
        content=f"**{request_data['prompt']}** - {interaction.user.mention} ({round(request.get_waiting_time(), 2)} + {round(request.get_processing_time(), 2)} {Localization(str()).get_localization('bot')['messages']['seconds']})",
        file=discord.File(os.path.join("cache", "txt2img", str(response_msg_id), "grid.jpg")), view=done_view)