import discord
from discord import Option
from discord.ext.commands import Cog

from modules import settings
from modules.config import Config
from modules.localization import Localization


class Settings(Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    settings_group = discord.SlashCommandGroup("settings")

    @settings_group.command(name='diffusing', description='Change default settings for diffusing')
    async def diffusing(self, ctx: discord.ApplicationContext,
                        neg_prompt: Option(str, name='neg_prompt', default=None, min_length=Config(str(), str()).get_values('limits')['diffuse']['neg_prompt']['min'], max_length=Config(str(), str()).get_values('limits')['diffuse']['neg_prompt']['max']),
                        steps: Option(int, name='steps', default=None, min_value=Config(str(), str()).get_values('limits')['diffuse']['steps']['min'], max_value=Config(str(), str()).get_values('limits')['diffuse']['steps']['max']),
                        count: Option(int, name='count', default=None, min_value=Config(str(), str()).get_values('limits')['diffuse']['count']['min'], max_value=Config(str(), str()).get_values('limits')['diffuse']['count']['max']),
                        seed: Option(int, name='seed', default=None),
                        cfg_scale: Option(float, name='cfg_scale', default=None, min_value=Config(str(), str()).get_values('limits')['diffuse']['cfg_scale']['min'], max_value=Config(str(), str()).get_values('limits')['diffuse']['cfg_scale']['max']),
                        res_x: Option(int, name='res_x', default=None, min_value=Config(str(), str()).get_values('limits')['diffuse']['res_x']['min'], max_value=Config(str(), str()).get_values('limits')['diffuse']['res_x']['max']),
                        res_y: Option(int, name='res_y', default=None, min_value=Config(str(), str()).get_values('limits')['diffuse']['res_y']['min'], max_value=Config(str(), str()).get_values('limits')['diffuse']['res_y']['max']),
                        sampler: Option(str, name='sampler', default=None, choices=Config(str(), str()).get_remote()['samplers']),
                        fast_mode: Option(bool, name='fast_mode', default=None, choices=[True, False])):
        user_id = str(ctx.interaction.user.id)

        changed_options = []
        if neg_prompt is not None:
            settings.Settings(str()).set_user(user_id, 'diffuse', 'neg_prompt', neg_prompt)
            changed_options.append('neg_prompt')
        if steps is not None:
            settings.Settings(str()).set_user(user_id, 'diffuse', 'steps', steps)
            changed_options.append('steps')
        if count is not None:
            settings.Settings(str()).set_user(user_id, 'diffuse', 'count', count)
            changed_options.append('count')
        if seed is not None:
            settings.Settings(str()).set_user(user_id, 'diffuse', 'seed', seed)
            changed_options.append('seed')
        if cfg_scale is not None:
            settings.Settings(str()).set_user(user_id, 'diffuse', 'cfg_scale', cfg_scale)
            changed_options.append('cfg_scale')
        if res_x is not None:
            settings.Settings(str()).set_user(user_id, 'diffuse', 'res_x', res_x)
            changed_options.append('res_x')
        if res_y is not None:
            settings.Settings(str()).set_user(user_id, 'diffuse', 'res_y', res_y)
            changed_options.append('res_y')
        if sampler is not None:
            settings.Settings(str()).set_user(user_id, 'diffuse', 'sampler', sampler)
            changed_options.append('sampler')
        if fast_mode is not None:
            settings.Settings(str()).set_user(user_id, 'diffuse', 'fast_mode', fast_mode)
            changed_options.append('fast_mode')

        await ctx.interaction.response.send_message(content='Successfully changed following default settings: `{}`'.format("`, `".join(changed_options)), ephemeral=True)

    @settings_group.command(name='upscaling', description='Change default settings for upscaling')
    async def upscaling(self, ctx: discord.ApplicationContext,
                        factor: Option(float, name='factor', default=None, min_value=Config(str(), str()).get_values('limits')['upscale']['factor']['min'], max_value=Config(str(), str()).get_values('limits')['upscale']['factor']['max']),
                        upscaler: Option(str, name='upscaler', default=None, choices=Config(str(), str()).get_remote()['upscalers'])):
        user_id = str(ctx.interaction.user.id)

        changed_options = []
        if factor is not None:
            settings.Settings(str()).set_user(user_id, 'upscale', 'factor', factor)
            changed_options.append('factor')
        if upscaler is not None:
            settings.Settings(str()).set_user(user_id, 'upscale', 'upscaler', upscaler)
            changed_options.append('upscaler')

        await ctx.interaction.response.send_message(content=Localization(str()).get_localization("bot")['messages']['settings_success'].format("`, `".join(changed_options)), ephemeral=True)
