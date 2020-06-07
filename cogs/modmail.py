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
        # If the message is in a dm channel and the author isn't the bot
        if type(message.channel) == discord.DMChannel and message.author != self.bot.user:
            
            match = re.match('^[0-9]+$', message.content)
            if match:
                return

            # Create list of guilds the bot shares with the user
            guilds = [g for g in self.bot.guilds if message.author in g.members]

            # Check function
            def check(m):
                # Checks if the author is the same in both messages
                return m.author == message.author

            # If guilds list isn't empty
            if guilds:

                # If guilds list has only one guild set it to guild var
                if len(guilds) == 1:
                    guild = guilds[0]

                # If guilds list has more than one guild
                else:
                    # Prompt user
                    await message.channel.send('You are in multiple servers with the bot. Enter the ID of the one you wish to contact.')

                    # Try to wait for response 
                    try:    
                        msg = await self.bot.wait_for('message', timeout=60, check=check)
                    
                    # Timeout after 60s
                    except:
                        await message.channel.send('Timeout: Please re-send your message.')

                    # Get guild from ID in response
                    guild = self.bot.get_guild(int(msg.content))

                # Get guild data from the db
                dbguild = self.bot.db.find_guild({'_id': guild.id})[0]

                # If the modmail channel isn't set, message user and return
                if not dbguild['modmail_channel_id']:
                    await message.channel.send('The server you sent has not set a modmail channel.')
                    return

                # Create and send embed to modmail channel
                mm_channel = guild.get_channel(dbguild['modmail_channel_id'])
                modrole = guild.get_role(dbguild['modrole_id'])
                embed = discord.Embed(colour=discord.Colour(0x2ecc71), description=message.content, timestamp=datetime.utcnow())
                embed.set_author(name=message.author, icon_url=message.author.avatar_url)
                embed.set_footer(text="modmail", icon_url=guild.icon_url)
                await mm_channel.send(content=modrole.mention, embed=embed)
                await message.channel.send('Your message has been sent. A moderator will contact you soon.')

            # If guilds list is empty, user shares no guilds with bot
            else:
                await message.channel.send("You don't share any servers with the bot")

    # Commands
    @is_staff()
    @commands.command()
    async def modmail(self, ctx, *args):
        if args[0] == 'set':
            channel = await discord.ext.commands.TextChannelConverter().convert(ctx, args[1])
            self.bot.db.update_guild({'_id': ctx.guild.id}, {'modmail_channel_id': channel.id})
            await ctx.send(f'Set modmail channel to {channel.mention}')

        elif args[0] == 'remove':
            self.bot.db.update_guild({'_id': ctx.guild.id}, {'modmail_channel_id': None})
            await ctx.send(f'Removed modmail from the server')
        
        # elif args[0] == 'reply':
        #     message = args[1]
    
