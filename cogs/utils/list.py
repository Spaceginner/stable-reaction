import discord
from discord.ext import commands

from modules.api.inference import API


class List(commands.Cog):
    command_group = discord.SlashCommandGroup("list")

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @command_group.command(name='samplers')
    async def samplers(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content=NotImplementedError)
        raise NotImplementedError

    @command_group.command(name='upscalers')
    async def upscalers(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content=NotImplementedError)
        raise NotImplementedError

    @command_group.command(name='models')
    async def models(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content=NotImplementedError)
        raise NotImplementedError

    @command_group.command(name='embeddings')
    async def embeddings(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content=NotImplementedError)
        raise NotImplementedError

    @command_group.command(name='hypernetworks')
    async def hypernetworks(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content=NotImplementedError)
        raise NotImplementedError

    @command_group.command(name='styles')
    async def styles(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content=NotImplementedError)
        raise NotImplementedError
