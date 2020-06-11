import json
import discord
from discord.ext import commands
from utils import is_staff


class ReactionRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Listeners
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.db.find_guild({'_id': payload.guild_id})[0]

        # If the message is in the list of msg ids associated with a reaction role in the db
        if str(payload.message_id) in guild['reaction_roles'] and not payload.member.bot:

            # Getting reaction role from db
            role = payload.member.guild.get_role(guild['reaction_roles'][str(payload.message_id)]['rrs'][payload.emoji.name])

            # Defining variables for later use
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            emojis = [emoji for emoji in guild['reaction_roles'][str(payload.message_id)]['rrs']]
            rtype = guild['reaction_roles'][str(payload.message_id)]['type']

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
                self.bot.db.update_guild({'_id': payload.guild_id}, guild)
                
            # If not unique or verify, add role
            else:
                await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        # Get db rrs
        rrs = self.bot.db.find_guild({'_id': payload.guild_id})[0]['reaction_roles']

        # If message id is in db rrs
        if str(payload.message_id) in rrs:

            # Get guild
            guild = discord.utils.get(self.bot.guilds, id=payload.guild_id)

            # Get rr role
            role = guild.get_role(rrs[str(payload.message_id)]['rrs'][payload.emoji.name])

            # Get member
            member = discord.utils.get(guild.members, id=payload.user_id)

            # Get rr type
            rtype = rrs[str(payload.message_id)]['type']

            # If rtype is normal or unique
            if rtype in ['normal', 'unique']:

                # If member has rr role
                if role in member.roles:

                    # Remove rr role
                    await member.remove_roles(role)

    # Commands
    @is_staff()
    @commands.command()
    async def rr(self, ctx, arg, *args):
        guild = self.bot.db.find_guild({'_id': ctx.guild.id})[0]
        if arg == 'add':
            channel = await discord.ext.commands.TextChannelConverter().convert(ctx, args[0])
            msg = await channel.fetch_message(args[1])
            rrs = {args[i]: args[i + 1] for i in range(2, len(args), 2)}

            for r in rrs:
                role = discord.utils.get(ctx.guild.roles, name=rrs[r])
                self.bot.db.add_reaction_role(ctx.guild.id, msg.id, {r: role.id})
                await msg.add_reaction(r)

            await ctx.send(f'Added reaction roles for **{args[1]}**')

        if arg == 'clear':
            msg = await ctx.fetch_message(args[0])
            rrs = guild['reaction_roles'][str(args[0])]['rrs']
            for r in rrs:
                await msg.clear_reaction(r)
            update = self.bot.db.find_guild({'_id': ctx.guild.id})[0]['reaction_roles']
            del update[str(args[0])]
            self.bot.db.update_guild(ctx.guild.id, {'reaction_roles': update})
            await ctx.send(f'Cleared reaction roles for **{args[0]}**')

        if arg in ['unique', 'verify', 'normal']:
            self.bot.db.update_rr_type(ctx.guild.id, args[0], arg)
            await ctx.send(f'Set message **{args[0]}** to {arg}')
