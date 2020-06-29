import discord
from discord.ext import commands
import logging
from utils import is_staff, not_staff, is_admin
from datetime import datetime


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# Listeners
    @commands.Cog.listener()
    async def on_member_join(self, member):
        roles = self.bot.db.get_guild(member.guild.id)['autoroles']
        await member.add_roles(*[member.guild.get_role(r) for r in roles])

# Commands

    @is_staff()
    @commands.command()
    async def autorole(self, ctx, role: discord.Role):
        roles = self.bot.db.get_guild(ctx.guild.id)['autoroles']
        roles.append(role.id)
        self.bot.db.update_guild(ctx.guild.id, {'autoroles': roles})
        for m in ctx.guild.members:
            await m.add_roles(role)
        await ctx.send(f'Added **{role}** to autoroles.')

    @is_staff()
    @commands.command()
    async def stickyrole(self, ctx, role: discord.Role):
        roles = self.bot.db.get_guild(ctx.guild.id)['sticky_roles']
        roles.append(role.id)
        self.bot.db.update_guild(ctx.guild.id, {'sticky_roles': roles})
        await ctx.send(f'Added **{role}** to sticky roles.')

    @is_staff()
    @commands.command()
    async def purge(self, ctx, amount=10):
        deleted = await ctx.channel.purge(limit=amount+1)
        await ctx.send(f'Deleted **{len(deleted)-1}** messages.', delete_after=5)

    @is_staff()
    @commands.command()
    async def mute(self, ctx, member: discord.Member, reason=None):
        modrole = ctx.guild.get_role(self.bot.db.get_guild(ctx.guild.id)['modrole_id'])
        if not_staff(modrole, member) or is_admin(ctx.author):
            muterole = ctx.guild.get_role(self.bot.db.get_guild(ctx.guild.id)['muterole_id'])
            await member.add_roles(muterole)
            await ctx.send(f'{member.mention} has been muted!')
            dbguild = self.bot.db.get_guild(ctx.guild.id)
            mlchannel = ctx.guild.get_channel(dbguild['modlog_channel_id'])
            case = len(dbguild['modlog_entries']) + 1
            p = dbguild['prefix']
            if reason == None:
                reason = f'No reason given, use `{p}reason {case} <text>` to add one'
            embed = discord.Embed(color=discord.Color(
                0xff5757), title=f'mute | case {case}', timestamp=datetime.utcnow())
            embed.add_field(name="Offender", value=f'{member}\n{member.mention}\n{member.id}')
            embed.add_field(name="Responsible Moderator", value=f'{ctx.author}\n{ctx.author.mention}\n{ctx.author.id}')
            embed.add_field(name="Reason", value=reason)
            msg = await mlchannel.send(embed=embed)
            dbguild['modlog_entries'].append(msg.id)
            self.bot.db.update_guild(ctx.guild.id, dbguild)
        else:
            await ctx.send(f'You lack the permissions to mute **{member}**!')
    
    @is_staff()
    @commands.command()
    async def warn(self, ctx, member: discord.Member, reason):
        modrole = ctx.guild.get_role(self.bot.db.get_guild(ctx.guild.id)['modrole_id'])
        if not modrole:
            await ctx.send('No modrole is set. Use the `modrole` command to set one.')
        elif not_staff(modrole, member) or is_admin(ctx.author):
            dbguild = self.bot.db.get_guild(ctx.guild.id)
            members = dbguild['members']
            members[str(member.id)]['warns']+=1
            self.bot.db.update_guild(ctx.guild.id, {'members': members})
            
            mlchannel = ctx.guild.get_channel(dbguild['modlog_channel_id'])
            case = len(dbguild['modlog_entries']) + 1

            embed = discord.Embed(color=discord.Color(
                0xe9ce62), title=f'warn | case {case}', timestamp=datetime.utcnow())
            embed.add_field(name="Offender", value=f'{member}\n{member.mention}\n{member.id}')
            embed.add_field(name="Responsible Moderator", value=f'{ctx.author}\n{ctx.author.mention}\n{ctx.author.id}')
            embed.add_field(name="Reason", value=reason)
            msg = await mlchannel.send(embed=embed)
            dbguild['modlog_entries'].append(msg.id)
            self.bot.db.update_guild(ctx.guild.id, dbguild)
            await ctx.send(f'**{member}** has been warned for {reason}!')
        else:
            await ctx.send(f'You lack the permissions to warn **{member}**!')

    # @commands.command()
    # async def warnlimit(self, ctx, punish, limit):
    #     if punish == 'mute':

    #     await ctx.send(f'I will now **{punish}** members after **{limit}** warnings.')

    @is_staff()
    @commands.command()
    async def unmute(self, ctx, member: discord.Member):
        modrole = ctx.guild.get_role(self.bot.db.get_guild(ctx.guild.id)['modrole_id'])
        if not_staff(modrole, member) or is_admin(ctx.author):
            muterole = ctx.guild.get_role(self.bot.db.get_guild(ctx.guild.id)['muterole_id'])
            await member.remove_roles(muterole)
            await ctx.send(f'{member.mention} has been unmuted!')
            dbguild = self.bot.db.get_guild(ctx.guild.id)
            mlchannel = ctx.guild.get_channel(dbguild['modlog_channel_id'])
            case = len(dbguild['modlog_entries']) + 1
            p = dbguild['prefix']
            if reason == None:
                reason = f'No reason given, use `{p}reason {case} <text>` to add one'
            embed = discord.Embed(color=discord.Color(
                0x2ecc71), title=f'unmute | case {case}', timestamp=datetime.utcnow())
            embed.add_field(name="Offender", value=f'{member}\n{member.mention}\n{member.id}')
            embed.add_field(name="Responsible Moderator", value=f'{ctx.author}\n{ctx.author.mention}\n{ctx.author.id}')
            embed.add_field(name="Reason", value=reason)
            msg = await mlchannel.send(embed=embed)
            dbguild['modlog_entries'].append(msg.id)
            self.bot.db.update_guild(ctx.guild.id, dbguild)
        else:
            await ctx.send(f'You lack the permissions to unmute {member.mention}! You cannot unmute moderators.')

    @is_staff()
    @commands.command()
    async def move(self, ctx, ch1: discord.VoiceChannel, ch2: discord.VoiceChannel):
        for member in ch1.members:
            await member.move_to(ch2)

    @commands.command()
    async def prefix(self, ctx, arg, prefix):
        if is_admin(ctx.author):
            prefixes = self.bot.db.get_guild(ctx.guild.id)['prefix']
            if prefixes != prefixes[0]:
                if arg == 'add':
                    if 0 < len(prefix) < 5:
                        prefixes.append(prefix)
                        self.bot.db.update_guild(ctx.guild.id, {'prefix': prefixes})
                        await ctx.send(f'Added **{prefix}** to prefixes.')
                    else:
                        await ctx.send(f'**{prefix}** is too long! Prefixes must be between 1 and 4 characters.')
                elif arg == 'remove':
                    prefixes.remove(prefix)
                    self.bot.db.update_guild(ctx.guild.id, {'prefix': prefixes})
                    await ctx.send(f'Removed **{prefix}** to prefixes.')
            else:
                await ctx.send(f"You can't alter the prefix **{prefix}**!")
        else:
            await ctx.send('You lack the permissions to set the server prefix!')

    @commands.command()
    async def muterole(self, ctx, role: discord.Role):
        if is_admin(ctx.author):
            if role in ctx.guild.roles:
                if role.name == '@everyone':
                    await ctx.send('You cannot make @everyone the muterole!')
                    return
                for tc in ctx.guild.text_channels:
                    await tc.set_permissions(role, send_messages=False)

                for vc in ctx.guild.voice_channels:
                    await vc.set_permissions(role, speak=False)

                for cat in ctx.guild.categories:
                    await cat.set_permissions(role, send_messages=False, speak=False)

                self.bot.db.update_guild(ctx.guild.id, {'muterole_id': role.id})
                await ctx.send(f'Mute role set to **{role}**')
        else:
            await ctx.send('You must be an admin to set the muterole!')
    
    
    @commands.command()
    async def mrupdate(self, ctx):
        if is_admin(ctx.author):
            muterole_id = self.bot.db.get_guild(ctx.guild.id)['muterole_id']
            if muterole_id != None:
                mute = ctx.guild.get_role(muterole_id)
                for tc in ctx.guild.text_channels:
                    await tc.set_permissions(mute, send_messages=False)

                for vc in ctx.guild.voice_channels:
                    await vc.set_permissions(mute, speak=False)

                for cat in ctx.guild.categories:
                    await cat.set_permissions(mute, send_messages=False, speak=False)

                await ctx.send(f'Success! The role **{mute}** has been updated with channel overrides!')

            else:
                await ctx.send('No muterole is set!')

    @commands.command()
    async def modrole(self, ctx, role: discord.Role):
        if is_admin(ctx.author):
            if role.name == '@everyone':
                await ctx.send('You cannot make everyone a mod!')
            else:
                self.bot.db.update_guild(ctx.guild.id, {'modrole_id': role.id})
                await ctx.send(f'Moderator role set to **{role}**')
        else:
            await ctx.send('You must be an admin to set the modrole!')

    @is_staff()
    @commands.command()
    async def verify(self, ctx, member: discord.Member, *msg_ids):
        g = self.bot.db.get_guild(ctx.guild.id)
        modrole = ctx.guild.get_role(g['modrole_id'])
        msgs = []
        for mid in msg_ids:
            msgs.append(await ctx.channel.fetch_message(mid))
        content = [msg.content for msg in msgs]
        if modrole in ctx.author.roles or is_admin(ctx.author):
            g['members'][str(member.id)]['verified'] = True
            self.bot.db.update_guild(ctx.guild.id, g)
            verify = ctx.guild.get_role(g['verify_role_id'])
            await member.add_roles(verify)
            channel = ctx.guild.get_channel(g['verify_log_channel_id'])
            if channel != None:
                embed = discord.Embed(colour=discord.Colour(0x2ecc71), timestamp=datetime.utcnow())
                embed.set_footer(text="Verification Log", icon_url=ctx.guild.icon_url)
                embed.add_field(name="Responsible Moderator:", value=ctx.author.mention, inline=False)
                embed.add_field(name="Member:", value=member.mention, inline=False)
                embed.add_field(name="Message:", value='\n'.join(content), inline=False)
                await channel.send(embed=embed)
            await ctx.message.delete()
            for msg in msgs:
                await msg.delete()

    @commands.command()
    async def verifyrole(self, ctx, role: discord.Role):
        if is_admin(ctx.author):
            self.bot.db.update_guild(ctx.guild.id, {'verify_role_id': role.id})
            await ctx.send(f'Set verification role to **{role.name}**')
        else:
            await ctx.send('You must be an admin to set the verify role!')

    @commands.command()
    async def verifylog(self, ctx, channel: discord.TextChannel):
        if is_admin(ctx.author):
            self.bot.db.update_guild(ctx.guild.id, {'verify_log_channel_id': channel.id})
            await ctx.send(f'Set verification channel to {channel.mention}')
        else:
            await ctx.send('You must be an admin to set the verify log!')
