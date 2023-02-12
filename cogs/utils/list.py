import discord
from discord.ext import commands

from modules.api.inference import API
from modules.localization import Localization


class List(commands.Cog):
    command_group = discord.SlashCommandGroup("list", description=Localization(str()).get_localization('descriptions')['list']['command'])

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @command_group.command(name='samplers', description=Localization(str()).get_localization('descriptions')['list']['prefix'].format('samplers'))
    async def samplers(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content=NotImplementedError)
        raise NotImplementedError

    @command_group.command(name='upscalers', description=Localization(str()).get_localization('descriptions')['list']['prefix'].format('upscalers'))
    async def upscalers(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content=NotImplementedError)
        raise NotImplementedError

    @command_group.command(name='models', description=Localization(str()).get_localization('descriptions')['list']['prefix'].format('models'))
    async def models(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content=NotImplementedError)
        raise NotImplementedError

    @command_group.command(name='embeddings', description=Localization(str()).get_localization('descriptions')['list']['prefix'].format('embeddings'))
    async def embeddings(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content=NotImplementedError)
        raise NotImplementedError

    @command_group.command(name='hypernetworks', description=Localization(str()).get_localization('descriptions')['list']['prefix'].format('hypernetworks'))
    async def hypernetworks(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content=NotImplementedError)
        raise NotImplementedError

    @command_group.command(name='styles', description=Localization(str()).get_localization('descriptions')['list']['prefix'].format('styles'))
    async def styles(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content=NotImplementedError)
        raise NotImplementedError
