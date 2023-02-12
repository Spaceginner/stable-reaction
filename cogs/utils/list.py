import discord
from discord import Option
from discord.ext import commands

from modules.api.inference import API
from modules.config import Config
from modules.localization import Localization


class List(commands.Cog):
    command_group = discord.SlashCommandGroup("list", description=Localization(str()).get_localization('bot')['descriptions']['list']['command'])

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @command_group.command(name='samplers', description=Localization(str()).get_localization('bot')['descriptions']['list']['prefix'].format('samplers'))
    async def samplers(self, ctx: discord.ApplicationContext):
        samplers_list = Config(str(), str()).get_remote()['samplers']

        await ctx.interaction.response.send_message(content=Localization(str()).get_localization('bot')['messages']['list_items'].format('samplers', '`, `'.join(samplers_list) if samplers_list else Localization(str()).get_localization('bot')['messages']['no_options']))

    @command_group.command(name='upscalers', description=Localization(str()).get_localization('bot')['descriptions']['list']['prefix'].format('upscalers'))
    async def upscalers(self, ctx: discord.ApplicationContext):
        upscalers_list = Config(str(), str()).get_remote()['upscalers']

        await ctx.interaction.response.send_message(content=Localization(str()).get_localization('bot')['messages']['list_items'].format('upscalers', '`, `'.join(upscalers_list) if upscalers_list else Localization(str()).get_localization('bot')['messages']['no_options']))

    @command_group.command(name='models', description=Localization(str()).get_localization('bot')['descriptions']['list']['prefix'].format('models'))
    async def models(self, ctx: discord.ApplicationContext):
        models_list = Config(str(), str()).get_remote()['models']

        await ctx.interaction.response.send_message(content=Localization(str()).get_localization('bot')['messages']['list_items'].format('models', '`, `'.join(models_list) if models_list else Localization(str()).get_localization('bot')['messages']['no_options']))

    @command_group.command(name='embeddings', description=Localization(str()).get_localization('bot')['descriptions']['list']['prefix'].format('embeddings'))
    async def embeddings(self, ctx: discord.ApplicationContext,
                         compatible: Option(bool, description='Show only embeddings which are compatible with the current models or all', choices=[True, False])
                         ):
        embeddings_list = Config(str(), str()).get_remote()['embeddings']['loaded']
        if not compatible:
            embeddings_list += Config(str(), str()).get_remote()['embeddings']['skipped']
        await ctx.interaction.response.send_message(content=Localization(str()).get_localization('bot')['messages']['list_items'].format('embeddings', '`, `'.join(embeddings_list) if embeddings_list else Localization(str()).get_localization('bot')['messages']['no_options']))

    @command_group.command(name='hypernetworks', description=Localization(str()).get_localization('bot')['descriptions']['list']['prefix'].format('hypernetworks'))
    async def hypernetworks(self, ctx: discord.ApplicationContext):
        hypernetworks_list = Config(str(), str()).get_remote()['hypernetworks']

        await ctx.interaction.response.send_message(content=Localization(str()).get_localization('bot')['messages']['list_items'].format('hypernetworks', '`, `'.join(hypernetworks_list) if hypernetworks_list else Localization(str()).get_localization('bot')['messages']['no_options']))

    @command_group.command(name='styles', description=Localization(str()).get_localization('bot')['descriptions']['list']['prefix'].format('styles'))
    async def styles(self, ctx: discord.ApplicationContext):
        styles_list = Config(str(), str()).get_remote()['styles']

        await ctx.interaction.response.send_message(content=Localization(str()).get_localization('bot')['messages']['list_items'].format('styles', '`, `'.join(styles_list) if styles_list else Localization(str()).get_localization('bot')['messages']['no_options']))
