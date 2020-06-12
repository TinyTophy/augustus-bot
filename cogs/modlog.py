from datetime import datetime

import discord
from discord.ext import commands
import asyncio

from utils import is_muted, is_staff, is_admin


class ModLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Listeners
    @commands.Cog.listener()
    async def on_member_ban(self, guild, member: discord.User):
        await asyncio.sleep(2)
        audit = [e async for e in guild.audit_logs(action=discord.AuditLogAction.ban)][0]
        dbguild = self.bot.db.find_guild(guild.id)
        mlchannel = guild.get_channel(dbguild['modlog_channel_id'])
        case = len(dbguild['modlog_entries']) + 1
        p = dbguild['prefix']
        if audit.reason == None:
            reason = f'No reason given, use `{p}reason {case} <text>` to add one'
        else:
            reason = audit.reason
        embed = discord.Embed(color=discord.Color(
            0xff5757), title=f'ban | case {case}', timestamp=audit.created_at)
        embed.add_field(name="Offender", value=f'{member}\n{member.mention}\n{member.id}')
        embed.add_field(name="Responsible Moderator", value=f'{audit.user.mention}\n{audit.user}')
        embed.add_field(name="Reason", value=reason)
        msg = await mlchannel.send(embed=embed)
        dbguild['modlog_entries'].append(msg.id)
        self.bot.db.update_guild(guild.id, dbguild)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member: discord.User):
        await asyncio.sleep(2)
        audit = [e async for e in guild.audit_logs(action=discord.AuditLogAction.unban)][0]
        dbguild = self.bot.db.find_guild(guild.id)
        mlchannel = guild.get_channel(dbguild['modlog_channel_id'])
        case = len(dbguild['modlog_entries']) + 1
        p = dbguild['prefix']
        if audit.reason == None:
            reason = f'No reason given, use `{p}reason {case} <text>` to add one'
        else:
            reason = audit.reason
        embed = discord.Embed(color=discord.Color(
            0x2ecc71), title=f'unban | case {case}', timestamp=audit.created_at)
        embed.add_field(name="Offender", value=f'{member}\n{member.mention}\n{member.id}')
        embed.add_field(name="Responsible Moderator", value=f'{audit.user.mention}\n{audit.user}')
        embed.add_field(name="Reason", value=reason)
        msg = await mlchannel.send(embed=embed)
        dbguild['modlog_entries'].append(msg.id)
        self.bot.db.update_guild(guild.id, dbguild)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await asyncio.sleep(2)
        audit = [e async for e in member.guild.audit_logs(action=discord.AuditLogAction.kick)][0]
        if audit.target == member:
            dbguild = self.bot.db.find_guild(member.guild.id)
            mlchannel = member.guild.get_channel(dbguild['modlog_channel_id'])
            case = len(dbguild['modlog_entries']) + 1
            if audit.reason == None:
                reason = f'No reason given, use `?reason {case} <text>` to add one'
            else:
                reason = audit.reason
            embed = discord.Embed(color=discord.Color(
                0xff5757), title=f'kick | case {case}', timestamp=audit.created_at)
            embed.add_field(name="Offender", value=f'{member}\n{member.mention}\n{member.id}')
            embed.add_field(name="Responsible Moderator", value=f'{audit.user.mention}\n{audit.user}')
            embed.add_field(name="Reason", value=reason)
            msg = await mlchannel.send(embed=embed)
            dbguild['modlog_entries'].append(msg.id)
            self.bot.db.update_guild(member.guild.id, dbguild)

    # Commands
    @is_staff()
    @commands.command()
    async def modlog(self, ctx, channel: discord.TextChannel):
        if is_admin(ctx.author):
            self.bot.db.update_guild(ctx.guild.id, {'modlog_channel_id': channel.id})
            await ctx.send(f'Set modlog channel to {channel.mention}')

    @is_staff()
    @commands.command()
    async def reason(self, ctx, case, *, reason):
        entries = self.bot.db.find_guild(ctx.guild.id)['modlog_entries']
        msg = await ctx.fetch_message(entries[case-1])

        msg.edit(embed=msg.embed)
