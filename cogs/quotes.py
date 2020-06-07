import discord
from discord.ext import commands
import random


class Quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def quote(self, ctx, member: discord.Member):
        quotes = self.bot.db.find_guild({'_id': ctx.guild.id})[0]['members'][str(member.id)]['quotes']
        if quotes:
            await ctx.send(random.choice(quotes))
        else:
            await ctx.send(f'**{member}** has no quotes.')

    @commands.command()
    async def addquote(self, ctx, member: discord.Member, *quote):
        q = ' '.join(quote)
        update = self.bot.db.find_guild({'_id': ctx.guild.id})[0]['members']
        update[str(member.id)]['quotes'].append(q)
        self.bot.db.update_guild({'_id': ctx.guild.id}, {'members': update})
        await ctx.send(f'Added **{q}** to db for **{member}**.')