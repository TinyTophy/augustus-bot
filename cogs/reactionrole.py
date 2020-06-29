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
        guild = self.bot.db.get_guild(payload.guild_id)

        if str(payload.message_id) in guild['rr_messages'] and not payload.member.bot:
            role = payload.member.guild.get_role(guild['rr_messages'][str(payload.message_id)]['reaction_roles'][payload.emoji.name])
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            emojis = [emoji for emoji in guild['rr_messages'][str(payload.message_id)]['reaction_roles']]
            rtype = guild['rr_messages'][str(payload.message_id)]['type']

            if rtype == 'unique':
                await payload.member.add_roles(role)
                for r in message.reactions:
                    if r.emoji in emojis and str(r.emoji) != str(payload.emoji):
                        users = await r.users().flatten()
                        if payload.member in users:
                            await message.remove_reaction(r.emoji, payload.member)

            elif rtype == 'verify':
                guild['members'][str(payload.member.id)]['verified'] = True
                await payload.member.add_roles(role)
                self.bot.db.update_guild(payload.guild_id, guild)

            else:
                await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        rr_messages = self.bot.db.get_guild(payload.guild_id)['rr_messages']

        if str(payload.message_id) in rr_messages:
            guild = discord.utils.get(self.bot.guilds, id=payload.guild_id)
            role = guild.get_role(rr_messages[str(payload.message_id)]['reaction_roles'][payload.emoji.name])
            member = discord.utils.get(guild.members, id=payload.user_id)
            rtype = rr_messages[str(payload.message_id)]['type']
            if rtype in ['normal', 'unique']:
                if role in member.roles:
                    await member.remove_roles(role)

# Commands

    @is_staff()
    @commands.command()
    async def rrtype(self, ctx, msg: discord.Message, rrtype):
        if rrtype in ['unique', 'verify', 'normal']:
            self.bot.db.update_rr(ctx.guild.id, msg.id, type=rrtype)
            await ctx.send(f'Set message **{msg.id}** to {rrtype}')
        else:
            await ctx.send(f'**{rrtype}** is not an accepted argument for this command!')

    @is_staff()
    @commands.command()
    async def rradd(self, ctx, channel:discord.TextChannel, msg: discord.Message, *args):
        rrs = {
            args[i]: await discord.ext.commands.RoleConverter().convert(ctx, args[i + 1]) 
            for i in range(0, len(args), 2)
        }
        rrs = {k: rrs[k].id for k in rrs}
        self.bot.db.add_rr(ctx.guild.id, msg.id, rrs)
        for emoji in rrs:
            await msg.add_reaction(emoji)

        await ctx.send(f'Added reaction roles for **{msg.id}**')
    
    @is_staff()
    @commands.command()
    async def rrclear(self, ctx, channel: discord.TextChannel, msg: discord.Message):
        rrs = self.bot.db.get_guild(ctx.guild.id)['rr_messages'][str(msg.id)]['reaction_roles']
        for emoji in rrs:
            await msg.clear_reaction(emoji)
        
        self.bot.db.remove_rr(ctx.guild.id, msg.id)
        await ctx.send(f'Cleared reaction roles for **{msg.id}**')