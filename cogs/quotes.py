import discord
from discord.ext import commands
import random


class Quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def quote(self, ctx, member: discord.Member):
        quotes = self.bot.db.get_member(member)['quotes']
        if quotes:
            await ctx.send(random.choice(quotes))
        else:
            await ctx.send(f'**{member}** has no quotes.')

    @commands.command()
    async def addquote(self, ctx, member: discord.Member, *, quote):
        quotes = self.bot.db.get_member(member)['quotes']
        quotes.append(quote)
        self.bot.db.update_member(member, quotes=quotes)
        await ctx.send(f'Added **{quote}** to db for **{member}**.')