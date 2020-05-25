import discord
from discord.ext import commands
from datetime import datetime

from utils import is_staff


class Modmail(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    # Listeners
    @commands.Cog.listener()
    async def on_message(self, message):
        if type(message.channel) == discord.DMChannel:
            if message.author != self.bot.user:
                guild = discord.utils.get(self.bot.guilds, id=679197184662437888)
                dbguild = self.db.find_guild({'_id': guild.id})[0]
                mm_channel = guild.get_channel(dbguild['modmail_channel_id'])
                modrole = guild.get_role(dbguild['modrole_id'])
                embed = discord.Embed(colour=discord.Colour(0x2ecc71), description=message.content, timestamp=datetime.utcnow())
                embed.set_author(name=message.author, icon_url=message.author.avatar_url)
                embed.set_footer(text="modmail", icon_url=guild.icon_url)
                await mm_channel.send(content=modrole.mention, embed=embed)

    # Commands
    @is_staff()
    @commands.command()
    async def mm(self, ctx, arg, *payload):
        if arg == 'set':
            channel = ctx.guild.get_channel(int(payload[0].strip('''<#>''')))
            self.db.update_guild(ctx.guild.id, modmail_channel_id=channel.id)
            await ctx.send(f'Set modmail channel to {channel.mention}')

        if arg == 'remove':
            self.db.update_guild(ctx.guild.id, modmail_channel_id='')
            # await self.bot.change_presence(activity=None)
            await ctx.send(f'Removed modmail from the server')
