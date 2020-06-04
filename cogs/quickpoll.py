import discord
from discord.ext import commands


class Quickpoll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# Commands

    # Quick poll command for non-staff users
    @commands.command()
    async def qp(self, ctx, *msg):
        embed = discord.Embed(title='Quick Poll', description=' '.join(msg), colour=discord.Colour(0x2ecc71))
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        message = await ctx.send(embed=embed)
        await message.add_reaction('✅')
        await message.add_reaction('❌')
        await ctx.message.delete()
