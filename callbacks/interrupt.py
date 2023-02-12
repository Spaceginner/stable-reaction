import discord

from modules.api import request_types, inference, queue
from modules.localization import Localization


async def interrupt_callback(interaction: discord.Interaction):
    api = inference.API(str())
    inference_queue = queue.Queue(int(), int())

    response_obj: discord.InteractionResponse = interaction.response

    response_msg_id, request_type_str, author_id = interaction.custom_id.split("-")
    author_id = int(author_id)

    if interaction.user.id != author_id:
        await response_obj.send_message(content=Localization(str()).get_localization('bot')['messages']['cancel_dismiss'], ephemeral=True)
        return

    request_type = request_types.convert(request_type_str)

    request = inference_queue.safe_get(response_msg_id, request_type)
    request.mark_interrupted()
    if not request.status.get()["is_processing"]:
        inference_queue.delete(response_msg_id, request_types.Text2Img)
    else:
        await api.interrupt()

    await response_obj.defer()
