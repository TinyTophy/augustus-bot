import discord
from discord.ext import commands
import logging
from datetime import datetime


class Log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot