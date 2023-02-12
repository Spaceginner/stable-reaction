import json
import os.path

import discord

from callbacks.regenerate import regenerate_callback
from callbacks.upscale import upscale_callback
from modules.api import request_types
from modules.localization import Localization


async def restore_callback(interaction: discord.Interaction):
    job_id, _ = interaction.custom_id.split("-")

    job_json = json.load(open(os.path.join('data', 'history', job_id)))
    job_data = job_json['data']
    job_type_str = job_json['type']

    job_type = request_types.convert(job_type_str)
    
    # request = None
    # if job_type is request_types.Text2Img:
    #     request = job_type(job_data['prompt'], job_data['negative_prompt'], job_data['steps'], job_data['batch_size'],
    #                        job_data['seed'], job_data['seed'], job_data['width'], job_data['height'], job_data['sampler_name'],
    #                        str(response_message.id), interaction.user.id, interaction.user.name, 1)
    # elif job_type is request_types.Upscale:
    #     request = job_type(job_data['image_index'], job_data['multiplier'], job_data['upscaler'], str(response_message.id),
    #                        job_data['base_id'], interaction.user.id, interaction.user.name, 3)

    # this is just the evilest hack i have ever done
    #                                       - Spaceginner

    interaction_hacked = interaction
    if job_type is request_types.Text2Img:
        interaction_hacked.custom_id = f'{job_id}-regen'

        await regenerate_callback(interaction_hacked)
    elif job_type is request_types.Upscale:
        interaction_hacked.custom_id = f'{job_data["image_index"]}-{job_id}-upscale'

        await upscale_callback(interaction_hacked)
