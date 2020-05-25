import asyncio
import json
import re
from datetime import datetime, timedelta
import discord
import humanize
from dateutil.relativedelta import relativedelta
from discord.ext import commands, tasks
from utils import is_staff


class Vote(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.vote_check.start()

# Listeners
    # Loop every 20 seconds
    @tasks.loop(seconds=20.0)
    async def vote_check(self):
        # Getting list of all guilds
        guilds = self.db.all_guilds()

        # For each guild
        for g in guilds:

            # For each vote in each guild
            for v in g['votes']:

                # grab the db guild object
                guild = discord.utils.get(self.bot.guilds, id=g['_id'])

                # get the members of the vote role
                role_members = [r.members for r in [
                    guild.get_role(rid) for rid in v['roles']]][0]

                # get vote message channel
                channel = discord.utils.get(
                    guild.text_channels, id=v['channel_id'])

                # get vote message
                message = await channel.fetch_message(v['message_id'])

                # get vote roles from vote
                roles = [guild.get_role(r) for r in v['roles']]

                # initialize vote count variables
                for_count = 0
                against_count = 0
                abstain_count = 0

                # for all reactions on the vote message
                for r in message.reactions:

                    # if reaction emoji is in the vote reactions
                    if r.emoji in ['✅', '❌', '⚪']:

                        # get the users who reacted
                        users = await r.users().flatten()

                        # convert users to members and iterate for each member
                        for m in [guild.get_member(uid) for uid in [u.id for u in users]]:

                            # a bool that says whether member has role
                            has_role = len(set(m.roles) & set(roles)) > 0

                            # check which vote the emoji represents if member has vote role
                            if r.emoji == '✅' and has_role:
                                for_count += 1
                            elif r.emoji == '❌' and has_role:
                                against_count += 1
                            elif r.emoji == '⚪' and has_role:
                                abstain_count += 1

                # Bool that says whether the vote status can be changed
                # If sufficient members with the role have voted, the vote may
                # not be able to be overturned. This will be false if autoclose
                # is set to false in the db.
                if g['autoclose_votes'] == True:
                    done = for_count > (len(role_members) - abstain_count) / 2 or against_count >= (len(role_members) - abstain_count) / 2
                else:
                    done = False

                # If the vote is either past time or the done bool is true
                if datetime.utcnow() >= v['end'] or done:

                    # Check who won and assign string status
                    if for_count > against_count:
                        status = 'Passed'
                    elif for_count < against_count:
                        status = 'Failed'
                    else:
                        status = 'Tied'

                    # Get embed from message
                    embed = message.embeds[0]

                    # Change title and footer to include status and set time to
                    # current time
                    embed.title = f'VOTE {status}'
                    embed.set_footer(text=f'Vote {status}')
                    embed.timestamp = datetime.utcnow()
                    await message.edit(embed=embed)

                    # Delete the vote from the database after sending the new embed
                    self.db.delete_vote(g['_id'], v)

    # Wait until bot is ready to run loop
    @vote_check.before_loop
    async def before_check(self):
        print('waiting...')
        await self.bot.wait_until_ready()

    # Deleting non-vote emojis to remove clutter
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        # Get db guild object
        guild = self.db.find_guild({'_id': payload.guild_id})[0]

        # Get payload channel
        channel = self.bot.get_channel(payload.channel_id)

        # Get payload message
        message = await channel.fetch_message(payload.message_id)

        # If the raw reaction is on a vote message
        if payload.message_id in [v['message_id'] for v in guild['votes']]:

            # If the raw reaction emoji isn't a vote emoji and the user isn't a bot
            if payload.emoji.name not in ['✅', '❌', '⚪'] and not payload.member.bot:

                # Remove the reaction from the votes
                await message.remove_reaction(payload.emoji, payload.member)

            # Else remove votes on more than one option
            else:
                message = await channel.fetch_message(payload.message_id)
                emojis = [r.emoji for r in message.reactions]
                for r in message.reactions:
                    if r.emoji in emojis and str(r.emoji) != str(payload.emoji) and not payload.member.bot:
                        users = await r.users().flatten()
                        if payload.member in users:
                            await message.remove_reaction(r.emoji, payload.member)

# Commands
    @is_staff()
    @commands.command()
    async def vote(self, ctx, msg, time_str='2d', *roles: (discord.Role)):

        # Using regex to convert time strings to datetime
        regex = re.compile(
            r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?', re.I)

        # Match the time string to the regex
        md = regex.match(time_str).groupdict()

        # For time unit (eg. days) in match, replace null values with 0
        for key in md:
            if md[key] is None:
                md[key] = 0

        # Convert each section to field in timedelta
        delta = timedelta(days=int(md['days']), hours=int(
            md['hours']), minutes=int(md['minutes']), seconds=int(md['seconds']))

        # Vote end datetime is current time plus delta
        vote_end = datetime.utcnow() + delta

        # Create embed for vote
        embed = discord.Embed(title='VOTE', description=msg,
                              colour=discord.Colour(0x2ecc71), timestamp=vote_end)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_footer(text='Vote Ends', icon_url=ctx.guild.icon_url)

        # If roles are empty or are only @everyone set content to empty string
        # to avoid pinging @everyone and set db roles to @everyone id
        if roles in [(), (ctx.guild.default_role)]:
            content = ''
            dbrs = [ctx.guild.default_role.id]

        # Else content is string of space-separated role mentions and db roles
        # is role.id for each role passed in
        else:
            content = ' '.join([r.mention for r in roles])
            dbrs = [r.id for r in roles]

        # Send message and add vote reactions
        message = await ctx.send(content=content, embed=embed)
        await message.add_reaction('✅')
        await message.add_reaction('❌')
        await message.add_reaction('⚪')

        # Assign vote dict for db and add it db
        vote = {
            'channel_id': ctx.channel.id,
            'message_id': message.id,
            'end': vote_end,
            'roles': dbrs
        }
        self.db.add_vote(ctx.guild.id, vote)

        # Delete command
        await ctx.message.delete()

    @commands.command()
    async def autoclose(self, ctx, condition: bool):
        self.db.update_guild({'_id': ctx.guild.id}, {'autoclose_votes': condition})
        await ctx.send(f'Set autoclose to **{condition}**.')
