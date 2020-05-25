import discord
from discord.ext import commands
import json


class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def embed(self, ctx, channel: discord.TextChannel, color: discord.Color, *, body):
        titledesc = body.split('|')
        embed = discord.Embed(
            color=color, title=titledesc[0], description=titledesc[1])
        await channel.send(embed=embed)
        await ctx.send(f'Created embed in **{channel}**')

    @commands.command()
    async def setfooter(self, ctx, msg: discord.Message, *, footer):
        embed = msg.embeds[0]
        embed.set_footer(text=footer, icon_url=ctx.guild.icon_url)
        await msg.edit(embed=embed)
