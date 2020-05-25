import json
import discord
from discord.ext import commands
from utils import is_staff


class ReactionRole(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    # Listeners
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.db.find_guild({'_id': payload.guild_id})[0]
        # If the message is in the list of msg ids associated with a reaction role in the db
        if str(payload.message_id) in guild['reaction_roles'] and not payload.member.bot:
            # Getting reaction role from db
            role = payload.member.guild.get_role(
                guild['reaction_roles'][str(payload.message_id)]['rrs'][payload.emoji.name])
            # Defining variables for later use
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            emojis = [emoji for emoji in guild['reaction_roles']
                      [str(payload.message_id)]['rrs']]
            rtype = guild['reaction_roles'][str(
                payload.message_id)]['type']

            # If the message is set to unique in the db
            if rtype == 'unique':
                # First add role
                await payload.member.add_roles(role)
                # For every reaction on the message
                for r in message.reactions:
                    if r.emoji in emojis and str(r.emoji) != str(payload.emoji):
                        users = await r.users().flatten()
                        if payload.member in users:
                            await message.remove_reaction(r.emoji, payload.member)

            elif rtype == 'verify':
                guild['members'][str(payload.member.id)]['verified'] = True
                await payload.member.add_roles(role)
                self.db.update_guild({'_id': payload.guild_id}, guild)
            # If not unique or verify, add role
            else:
                await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        rrs = self.db.find_guild({'_id': payload.guild_id})[
            0]['reaction_roles']
        if str(payload.message_id) in rrs:
            rtype = rrs[str(payload.message_id)]['tyfor r in message.reactions:for r in message.reactions:pe']
            guild = discord.utils.get(self.bot.guilds, id=payload.guild_id)
            role = guild.get_role(
                rrs[str(payload.message_id)]['rrs'][payload.emoji.name])
            member = discord.utils.get(guild.members, id=payload.user_id)
            if rtype in ['normal', 'unique']:
                if role in member.roles:
                    await member.remove_roles(role)

    # Commands
    @is_staff()
    @commands.command()
    async def rr(self, ctx, arg, *payload):
        guild = self.db.find_guild({'_id': ctx.guild.id})[0]
        if arg == 'add':
            channel = ctx.guild.get_channel(int(payload[0].strip('''<#>''')))
            msg = await channel.fetch_message(payload[1])
            rrs = {payload[i]: payload[i + 1]
                   for i in range(2, len(payload), 2)}

            for r in rrs:
                role = discord.utils.get(ctx.guild.roles, name=rrs[r])
                rr = {r: role.id}
                self.db.add_reaction_role({'_id': ctx.guild.id}, msg.id, rr)
                await msg.add_reaction(r)

            await ctx.send(f'Added reaction roles for **{payload[1]}**')

        if arg == 'clear':
            msg = await ctx.fetch_message(payload[0])
            rrs = guild['reaction_roles'][str(payload[0])]['rrs']
            for r in rrs:
                await msg.clear_reaction(r)
            update = self.db.find_guild({'_id': ctx.guild.id})[
                0]['reaction_roles']
            del update[str(payload[0])]
            self.db.update_guild({'_id': ctx.guild.id}, {
                                 'reaction_roles': update})
            await ctx.send(f'Cleared reaction roles for **{payload[0]}**')

        if arg in ['unique', 'verify', 'normal']:
            self.db.update_rr_type({'_id': ctx.guild.id}, payload[0], arg)
            await ctx.send(f'Set message **{payload[0]}** to {arg}')
