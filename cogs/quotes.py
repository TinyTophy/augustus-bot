import discord
from discord.ext import commands
import random
from datetime import datetime


class Quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def quote(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        quotes = self.bot.db.get_member(member).quotes
        if quotes:
            quote = random.choice(quotes)
            msg = quote['msg']
            embed = discord.Embed(color=member.color, description=f'"{msg}"', timestamp=quote['time'])
            embed.set_author(name=member, icon_url=member.avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'**{member}** has no quotes.')

    @commands.command()
    async def addquote(self, ctx, member: discord.Member, *, quote):
        quotes = self.bot.db.get_member(member).quotes
        quote = {'msg': quote, 'time': datetime.utcnow()}
        quotes.append(quote)
        self.bot.db.update_member(member, quotes=quotes)
        await ctx.send(f'Added **{quote["msg"]}** to quotes for **{member}**.')