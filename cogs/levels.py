import discord
from discord.ext import commands
from utils import is_staff


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    @commands.command()
    async def level(self, ctx, member=None):
        pass

    @is_staff()
    @commands.command()
    async def rank(self, ctx, level: int, role: discord.Role):
        update = self.bot.db.find_guild({'_id': ctx.guild.id})[0]
        ranks = update['ranks']
        ranks[str(role.id)] = level
        self.bot.db.update_guild({'_id': ctx.guild.id}, {'ranks': ranks})
        await ctx.send(f'Users will now get the **{role}** role when they reach level **{level}**.')