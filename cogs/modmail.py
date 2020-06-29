import discord
from discord.ext import commands
from datetime import datetime
import re

from utils import is_staff


class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Listeners
    @commands.Cog.listener()
    async def on_message(self, message):
        if type(message.channel) == discord.DMChannel and message.author.bot:
            match = re.match('^[0-9]+$', message.content)
            if match:
                return

            guilds = [g for g in self.bot.guilds if message.author in g.members]

            if guilds:
                if len(guilds) == 1:
                    guild = guilds[0]
                else:
                    await message.channel.send('You are in multiple servers with the bot. Enter the ID of the one you wish to contact.')
                    try:
                        msg = await self.bot.wait_for('message', timeout=60, check=lambda m: m.author == message.author)
                    except:
                        await message.channel.send('Timeout: Please re-send your message.')
                    guild = self.bot.get_guild(int(msg.content))

                dbguild = self.bot.db.get_guild(guild.id)
                if not dbguild['modmail_channel_id']:
                    await message.channel.send('The server you sent has not set a modmail channel.')
                    return

                mm_channel = guild.get_channel(dbguild['modmail_channel_id'])
                modrole = guild.get_role(dbguild['modrole_id'])
                embed = discord.Embed(colour=discord.Colour(0x2ecc71), description=message.content, timestamp=datetime.utcnow())
                embed.set_author(name=message.author, icon_url=message.author.avatar_url)
                embed.set_footer(text="modmail", icon_url=guild.icon_url)
                await mm_channel.send(content=modrole.mention, embed=embed)
                await message.channel.send('Your message has been sent. A moderator will contact you soon.')

            else:
                await message.channel.send("You don't share any servers with the bot")

    # Commands
    @is_staff()
    @commands.command()
    async def modmail(self, ctx, *args):
        if args[0] == 'set':
            channel = await discord.ext.commands.TextChannelConverter().convert(ctx, args[1])
            self.bot.db.update_guild(ctx.guild.id, modmail_channel_id=channel.id)
            await ctx.send(f'Set modmail channel to {channel.mention}')

        elif args[0] == 'remove':
            self.bot.db.update_guild(ctx.guild.id, modmail_channel_id=None)
            await ctx.send(f'Removed modmail from the server')

    
