import discord
from discord.ext import commands

from modules.localization import Localization


class Ping(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="ping", description=Localization(str()).get_localization("bot")["descriptions"]["ping"]["command"])
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.interaction.response.send_message(content=Localization(str()).get_localization("bot")["messages"]["pong"])
