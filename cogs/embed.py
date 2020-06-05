import discord
from discord.ext import commands, flags
import json
from datetime import datetime


class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @flags.add_flag("--title", type=str, default='Embed')
    @flags.add_flag("--author")
    @flags.add_flag("--color")
    @flags.add_flag("--desc")
    @flags.add_flag("--url")
    @flags.add_flag("--thumbnail")
    @flags.add_flag("--image")
    @flags.add_flag("--footer")
    @flags.add_flag("--timestamp", type=bool, default=False)
    @flags.command()
    async def embed(self, ctx, channel: discord.TextChannel, **flags):
        print(flags)
        embed = discord.Embed(title=flags['title'])

        if flags['author']:
            author = list(map(str, flags['author'].split(',')))

            if len(author) >= 2 and author[1].lower() == 'none':
                author[1] = discord.Embed.Empty 

            embed.set_author(name=author[0], url=author[1] if len(
                author) >= 2 else discord.Embed.Empty, icon_url=author[2] if len(author) >= 3 else discord.Embed.Empty)

        if flags['color']:
            embed.color = discord.Color(int(flags['color'], 16))

        if flags['desc']:
            embed.description = flags['desc']

        if flags['footer']:
            embed.set_footer(text=flags['footer'], icon_url=ctx.guild.icon_url)
        
        if flags['timestamp']:
            embed.timestamp = datetime.utcnow()

        await channel.send(embed=embed)
        await ctx.send(f'Created embed in **{channel}**')
