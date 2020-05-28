import discord
from discord.ext import commands
import logging
from utils import is_staff, not_staff, is_admin
from datetime import datetime


class Log(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db