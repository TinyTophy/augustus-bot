import discord
from discord.ext import commands

from utils import is_staff

class Levels(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    @commands.command()
    async def level(self, ctx, member=None):
        pass

    