import asyncio
import json
import os.path
import sys
import threading

import discord
import requests
import yaml
from discord import Option

from modules.api import request_types, inference
from modules import queue, settings


async def launch(inference_queue: queue.Queue, config: dict):
    print("Starting...")

    # Discord bot instance and events listeners
    bot = discord.Bot(debug_guilds=[])

    @bot.event
    async def on_ready():
        print("Discord bot is launched")

    # Bot interaction callbacks
    async def upscale_callback(interaction: discord.Interaction):
        parsed_custom_id = interaction.custom_id.split("-")

        base_msg_id = int(parsed_custom_id[0])
        base_image_index = int(parsed_custom_id[1])
        request_type = parsed_custom_id[2]

        with open(os.path.join("request_history", str(base_msg_id), f"{request_type}.json"), 'r') as file_stream:
            base_image_prompt = json.load(file_stream)["prompt"]

        await interaction.response.send_message(content=f"Upscaling image #{base_image_index + 1} with **{base_image_prompt}** - {interaction.user.mention}")

        response_object = await interaction.original_response()

        request = request_types.Upscale(request_type, base_image_index, 4, "RealESRGAN", response_object, base_msg_id, 3)
        inference_queue.put(request)

        while request.status.get()["is_processing"] is False and not request.status.get()["is_interrupted"]:
            place = request.status.get()["place"]
            await interaction.edit_original_response(content=f"Upscaling image #{base_image_index + 1} with **{base_image_prompt}** - {interaction.user.mention} (`Waiting in a queue{f': {place}' if place is not None else ''}`)")
            await asyncio.sleep(0.075)

        while request.status.get()["is_finished"] is False:
            await interaction.edit_original_response(content=f"Upscaling image #{base_image_index + 1} with **{base_image_prompt}** — {interaction.user.mention} (`Processing...`)")
            await asyncio.sleep(0.075)

        await response_object.edit(content=f"Upscaled image #{base_image_index + 1} with **{base_image_prompt}** - {interaction.user.mention} (`complete in {round(request.get_waiting_time(), 2)} + {round(request.get_processing_time(), 2)} seconds`)",
                                   file=discord.File(os.path.join("temp", str(base_msg_id), "upscaling", f"image_{request.options.get()['image_index']}.png")))
        await interaction.followup.send(ephemeral=True, delete_after=3, content=f"{interaction.user.mention}, upscaling of an image #{base_image_index + 1} with a prompt **{base_image_prompt}** is finished!")

    # TODO add 'Restore' button
    # TODO add support for any other requests
    async def interrupt_callback(interaction: discord.Interaction):
        parsed_custom_id = interaction.custom_id.split("-")

        response_msg_id = parsed_custom_id[0]
        request_type = parsed_custom_id[1]

        inference_type = request_types.Text2Img
        if request_type == "txt2img":
            inference_type = request_types.Text2Img

        request = inference_queue.safe_get(response_msg_id, inference_type)

        request.mark_interrupted()

        request_prompt = request.options.get()["prompt"]

        inference_queue.delete(response_msg_id, request_types.Text2Img, config["inference"]["webui_url"])

        await request.response_object.edit(content=f"Image generation for a prompt **{request_prompt}** - {interaction.user.mention} was interrupted", view=discord.ui.View())

    async def change_settings_callback(interaction: discord.Interaction):
        pass

    # Bot commands
    @bot.slash_command(name="diffuse", description="Generate images based of *your* prompt")
    async def diffuse(ctx: discord.ApplicationContext,
                      prompt: Option(str, "The prompt which will be used to generate images"),
                      neg_prompt: Option(str, "What don't you want to see in images", default=""),
                      steps: Option(int, "In how many steps will be images processed", default=15, min_value=10, max_value=100),
                      count: Option(int, "How many images to generate", min_value=2, max_value=4, default=2),
                      seed: Option(int, "What seed will be used to generate images; same seed gives same images", default=-1),
                      cfg_scale: Option(float, "How much model will be guided by your prompt, default is 7", default=7, min_value=0, max_value=30),
                      width: Option(int, "Width of generated images in pixels", default=512, min_value=256, max_value=1536),
                      height: Option(int, "Height of images generated in pixels", default=512, min_value=256, max_value=1536),
                      sampler: Option(str, "Method (sampler) which will be used to generate images", choices=config["remote"]["samplers"], default="Euler a"),
                      fast_mode: Option(bool, "Will prioritize your request", choices=[False, True], default=False)
                      ):
        await ctx.interaction.response.send_message(content=f"**{prompt}** — {ctx.interaction.user.mention} (`Waiting in a queue`)")

        await settings.prepare_settings(ctx.interaction.user.id, ctx.interaction.guild_id, config["inference"]["defaults"])

        response_msg = await ctx.interaction.original_response()

        interrupt_button = discord.ui.Button(label="Interrupt", custom_id=f"{response_msg.id}-txt2img", style=discord.ButtonStyle.danger)
        interrupt_button.callback = interrupt_callback
        progress_view = discord.ui.View(interrupt_button)

        await ctx.interaction.edit_original_response(content=f"**{prompt}** — {ctx.interaction.user.mention} (`Waiting in a queue`)", view=progress_view)

        request = request_types.Text2Img(prompt, neg_prompt, steps, count, seed, cfg_scale, width, height, sampler, response_msg, response_msg.id, prioritization=1 if not fast_mode else 2)
        inference_queue.put(request)

        while request.status.get()["is_processing"] is False and not request.status.get()["is_interrupted"]:
            place = request.status.get()["place"]
            await ctx.interaction.edit_original_response(content=f"**{prompt}** — {ctx.interaction.user.mention} (`Waiting in a queue: {'N/A' if place is None else place}`)")
            await asyncio.sleep(0.075)

        progress = inference.progress(config["inference"]["webui_url"])
        while (progress == 0 or progress == 0.01) and not request.status.get()["is_interrupted"]:
            await ctx.interaction.edit_original_response(content=f"**{prompt}** — {ctx.interaction.user.mention} (`Waiting to start`)")
            progress = inference.progress(config["inference"]["webui_url"])
            await asyncio.sleep(0.075)

        previous_progress = inference.progress(config["inference"]["webui_url"])
        while request.status.get()["is_finished"] is False and not request.status.get()["is_interrupted"]:
            is_finishing = False
            if not is_finishing:
                progress = inference.progress(config["inference"]["webui_url"])
            if previous_progress > progress or round(progress, 2) == 0.94 or is_finishing:
                is_finishing = True
                progress = 1
            if progress != 1:
                await ctx.interaction.edit_original_response(content=f"**{prompt}** — {ctx.interaction.user.mention} (`{'N/A ' if progress is None or progress == 0.01 else round(progress * 100)}%`)")
            else:
                await ctx.interaction.edit_original_response(content=f"**{prompt}** — {ctx.interaction.user.mention} (`Finishing...`)")
            await asyncio.sleep(0.075)
            if not is_finishing:
                previous_progress = inference.progress(config["inference"]["webui_url"])

        if not request.status.get()["is_interrupted"]:
            result_view_items = []
            for index in range(count):
                button = discord.ui.Button(label=f"U{index + 1}", row=0, custom_id=f"{response_msg.id}-{index}-txt2img")
                button.callback = upscale_callback

                result_view_items.append(button)
            result_view = discord.ui.View(*result_view_items)

            await ctx.interaction.edit_original_response(content=f"**{prompt}** - {ctx.interaction.user.mention} (complete in `{round(request.get_waiting_time(), 2)} + {round(request.get_processing_time(), 2)} seconds`)",
                           file=discord.File(os.path.join("temp", str(response_msg.id), "txt2img", "grid.jpg")), view=result_view)
            await ctx.interaction.followup.send(ephemeral=True, delete_after=3, content=f"{ctx.interaction.user.mention}, image generation with a prompt **{prompt}** is finished!")

    # TODO make it
    @bot.slash_command(name="settings", description="Manage your settings")
    async def change_settings(ctx: discord.ApplicationContext):
        await settings.prepare_settings(ctx.interaction.user.id, ctx.interaction.guild_id, config["inference"]["defaults"])

        view = discord.ui.View(discord.ui.Select(options=[discord.SelectOption(label="Diffusing", description="Change settings for /diffuse command", value="diffuse"),
                                                          discord.SelectOption(label="Upscaling", description="Change settings for upscaling", value="upscale")]))

        await ctx.interaction.response.send_message(ephemeral=True, content="Select what category of settings you want to change:", view=view)

    @bot.slash_command(name="ping", description="If the bot doesn't say it is alive... R.I.P. bot")
    async def ping(ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content="Pong! I am alive!", ephemeral=True)

    # Launching bot
    print("Launching bot... ")
    await bot.start(config["bot"]["token"])


def interrupt_handler(exit_event: threading.Event, interruptions_exit: int):
    interrupt_counter = 0

    while interrupt_counter < interruptions_exit:
        try:
            if exit_event.is_set():
                break
        except KeyboardInterrupt:
            interrupt_counter += 1

    if interrupt_counter >= interruptions_exit:
        print("Keyboard interruption occurred >3 times, hard exiting...")
        sys.exit(2)


def main():
    print("Press CRTL + C to exit\n")

    # Loading configs
    try:
        config = yaml.safe_load(open("config.yaml", "r"))
        config["remote"] = {}


    except Exception as e:
        print(e)
        input("Press ENTER to exit...")
        sys.exit()

    if config["inference"]["webui_url"][-1] == "/":
        config["inference"]["webui_url"] = config["inference"]["webui_url"][:-1]

    try:
        config["remote"]["samplers"] = inference.samplers(config["inference"]["webui_url"])
        config["remote"]["settings"] = inference.get_settings(config["inference"]["webui_url"])
    except requests.exceptions.ConnectionError:
        print("\nRunning installation of AUTOMATIC1111's WebUI is not found.")
        print("You can check 2 following things:")
        print("\tYou run WebUI with --api argument")
        print("\tYou typed WebUI url correctly in bot.yaml file")
        input("\nPress ENTER to exit...")
        sys.exit(-1)

    if config["inference"]["settings"]["disable_watermark"]:
        inference.set_setting(config["inference"]["webui_url"], "do_not_add_watermark", True)

    # Setting up a queue
    api_request_queue = queue.Queue(45, 10)

    queue_processor_thread = threading.Thread(target=api_request_queue.process, args=(config["inference"]["webui_url"],))
    queue_requests_updater_thread = threading.Thread(target=api_request_queue.update_requests)

    queue_processor_thread.start()
    queue_requests_updater_thread.start()

    # Needed for a less cluttered exiting
    try:
        asyncio.run(launch(api_request_queue, config))
    except KeyboardInterrupt:
        print("Exiting...")

    exit_event = threading.Event()
    interrupt_handler_thread = threading.Thread(target=interrupt_handler, args=(exit_event, 3))
    interrupt_handler_thread.start()

    api_request_queue.put(None)
    while True:
        try:
            queue_processor_thread.join()
            queue_requests_updater_thread.join()

            break
        except KeyboardInterrupt:
            pass

    exit_event.set()


if __name__ == "__main__":
    main()
