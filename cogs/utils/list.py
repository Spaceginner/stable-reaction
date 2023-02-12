import discord
from discord.ext import commands

from modules.api.inference import API


class List(commands.Cog):
    command_group = discord.SlashCommandGroup("list")

    def __init__(self, bot: discord.Bot):
        self.bot = bot
