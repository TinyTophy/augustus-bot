import discord
from discord.ext import commands
from utils import is_staff


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    