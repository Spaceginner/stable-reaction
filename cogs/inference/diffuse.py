import asyncio
import os

import discord
from discord import Option
from discord.ext import commands

from callbacks.interrupt import interrupt_callback
from callbacks.regenerate import regenerate_callback
from callbacks.upscale import upscale_callback
from callbacks.utils.show_info import show_info_callback
from callbacks.utils.show_original import show_original_callback
from modules.config import Config
from modules.localization import Localization
from modules.api import inference, request_types, queue
from modules.settings import Settings


async def restore_callback(interaction: discord.Interaction):
    job_id, _ = interaction.custom_id.split("-")

    interaction_hacked = interaction
    interaction_hacked.custom_id = f'{job_id}-regen'

    await regenerate_callback(interaction_hacked)


class Diffuse(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="diffuse", description=Localization(str()).get_localization("bot")["descriptions"]["diffuse"]["command"])
    async def diffuse(self, ctx: discord.ApplicationContext,
                      prompt: Option(str, Localization(str()).get_localization("bot")["descriptions"]["diffuse"]["arguments"]["prompt"], min_length=Config(str(), str()).get_values('limits')['diffuse']['prompt']['min'], max_length=Config(str(), str()).get_values('limits')['diffuse']['prompt']['max']),
                      neg_prompt: Option(str, Localization(str()).get_localization("bot")["descriptions"]["diffuse"]["arguments"]["neg_prompt"], min_length=Config(str(), str()).get_values('limits')['diffuse']['neg_prompt']['min'], default=None, max_length=Config(str(), str()).get_values('limits')['diffuse']['neg_prompt']['max']),
                      steps: Option(int, Localization(str()).get_localization("bot")["descriptions"]["diffuse"]["arguments"]["steps"], default=None, min_value=Config(str(), str()).get_values('limits')['diffuse']['steps']['min'], max_value=Config(str(), str()).get_values('limits')['diffuse']['steps']['max']),
                      count: Option(int, Localization(str()).get_localization("bot")["descriptions"]["diffuse"]["arguments"]["count"], min_value=Config(str(), str()).get_values('limits')['diffuse']['count']['min'], max_value=Config(str(), str()).get_values('limits')['diffuse']['count']['max'], default=None),
                      seed: Option(int, Localization(str()).get_localization("bot")["descriptions"]["diffuse"]["arguments"]["seed"], default=None),
                      cfg_scale: Option(float, Localization(str()).get_localization("bot")["descriptions"]["diffuse"]["arguments"]["cfg_scale"], default=None, min_value=Config(str(), str()).get_values('limits')['diffuse']['cfg_scale']['min'], max_value=Config(str(), str()).get_values('limits')['diffuse']['cfg_scale']['max']),
                      res_x: Option(int, Localization(str()).get_localization("bot")["descriptions"]["diffuse"]["arguments"]["res_x"], default=None, min_value=Config(str(), str()).get_values('limits')['diffuse']['res_x']['min'], max_value=Config(str(), str()).get_values('limits')['diffuse']['res_x']['max']),
                      res_y: Option(int, Localization(str()).get_localization("bot")["descriptions"]["diffuse"]["arguments"]["res_y"], default=None, min_value=Config(str(), str()).get_values('limits')['diffuse']['res_y']['min'], max_value=Config(str(), str()).get_values('limits')['diffuse']['res_y']['max']),
                      sampler: Option(str, Localization(str()).get_localization("bot")["descriptions"]["diffuse"]["arguments"]["sampler"], choices=Config(str(), str()).get_remote()["samplers"], default=None),
                      fast_mode: Option(bool, Localization(str()).get_localization("bot")["descriptions"]["diffuse"]["arguments"]["fast_mode"], choices=[False, True], default=Config(str(), str()).get_values('defaults')['diffuse']['fast_mode'])
                      ):
        user_id = str(ctx.interaction.user.id)
        user_settings = Settings(str()).get_user(user_id)['diffuse']
        if neg_prompt is None:
            neg_prompt = user_settings['neg_prompt']
        if steps is None:
            steps = user_settings['steps']
        if count is None:
            count = user_settings['count']
        if seed is None:
            seed = user_settings['seed']
        if cfg_scale is None:
            cfg_scale = user_settings['cfg_scale']
        if res_x is None:
            res_x = user_settings['res_x']
        if res_y is None:
            res_y = user_settings['res_y']
        if sampler is None:
            sampler = user_settings['sampler']
        if fast_mode is None:
            fast_mode = user_settings['fast_mode']

        api = inference.API(str())
        inference_queue = queue.Queue(int(), int())

        await ctx.interaction.response.send_message(content=f"**{prompt}** - {ctx.interaction.user.mention} ({Localization(str()).get_localization('bot')['messages']['queue_wait']}...)")

        response_msg = await ctx.interaction.original_response()
        response_msg_id = response_msg.id

        request = request_types.Text2Img(prompt, neg_prompt, steps, count, seed, cfg_scale, res_x, res_y, sampler, response_msg_id, ctx.interaction.user.id, ctx.interaction.user.name, 1 if not fast_mode else 2)
        inference_queue.put(request)

        interrupt_button = discord.ui.Button(label=Localization(str()).get_localization('bot')['messages']['cancel'], custom_id=f"{response_msg_id}-txt2img-{ctx.interaction.user.id}", style=discord.ButtonStyle.danger)
        interrupt_button.callback = interrupt_callback

        while not request.status.get()["is_processing"] and not request.status.get()["is_interrupted"]:
            place = request.status.get()["place"]
            await response_msg.edit(content=f"**{prompt}** - {ctx.interaction.user.mention} ({Localization(str()).get_localization('bot')['messages']['queue_wait']}{f': {place}' if place else '...'})", view=discord.ui.View(interrupt_button, timeout=None))
            await asyncio.sleep(0.075)

        while not request.status.get()["is_finished"] and not request.status.get()["is_interrupted"]:
            request.progress.set_progress(await api.progress())
            await response_msg.edit(content=f"**{prompt}** - {ctx.interaction.user.mention} ({request.progress})")
            await asyncio.sleep(0.075)

        if request.status.get()["is_interrupted"]:
            cancelled_view_items = []

            restore_button = discord.ui.Button(label='Restore', custom_id=f'{response_msg_id}-restore')
            restore_button.callback = restore_callback

            cancelled_view_items.append(restore_button)

            await response_msg.edit(f"**{prompt}** - {ctx.interaction.user.mention} ({Localization(str()).get_localization('bot')['messages']['cancelled']})", view=discord.ui.View(*cancelled_view_items))
            return

        done_view_items = []

        # Upscale button
        for index in range(count):
            button = discord.ui.Button(label=f"U{index + 1}", row=0, custom_id=f"{index}-{response_msg_id}-upscale")
            button.callback = upscale_callback

            done_view_items.append(button)

        # Show original button
        for index in range(count):
            button = discord.ui.Button(label=f"S{index + 1}", row=1, custom_id=f"{index}-{response_msg_id}-original")
            button.callback = show_original_callback

            done_view_items.append(button)

        # Regenerate button
        button = discord.ui.Button(label="Regen", row=0, custom_id=f"{response_msg_id}-regen")
        button.callback = regenerate_callback
        done_view_items.append(button)

        # Info button
        button = discord.ui.Button(label="Info", row=1, custom_id=f"txt2img-{response_msg_id}-info")
        button.callback = show_info_callback
        done_view_items.append(button)

        done_view = discord.ui.View(*done_view_items, timeout=None)

        await response_msg.edit(content=f"**{prompt}** - {ctx.interaction.user.mention} ({round(request.get_waiting_time(), 2)} + {round(request.get_processing_time(), 2)} {Localization(str()).get_localization('bot')['messages']['seconds']})",
                                file=discord.File(os.path.join("cache", "txt2img", str(response_msg_id), "grid.jpg")), view=done_view)
