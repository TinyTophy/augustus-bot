from discord.ext import commands
import discord
from dateutil.relativedelta import relativedelta
import json


def is_staff():
    def predicate(ctx):
        modrole = ctx.guild.get_role(ctx.cog.bot.db.find_guild(ctx.guild.id)['modrole_id'])
        return modrole in ctx.author.roles or ctx.author.guild_permissions.administrator
    return commands.check(predicate)

def not_staff(modrole, target):
    return modrole not in target.roles and not target.guild_permissions.administrator

def is_admin(member):
    return member.guild_permissions.administrator

def is_muted(member, muterole):
    return muterole in member.roles

def get_prefix(bot, message):
    if type(message.channel) == discord.TextChannel:
        return bot.db.find_guild(message.guild.id)['prefix']
    else:
        return ['!']

def pretty_delta(delta):
    pdelta = {}
    if delta.years > 0:
        pdelta['years'] = delta.years
    if delta.months > 0:
        pdelta['months'] = delta.months
    if delta.days > 0:
        pdelta['days'] = delta.days
    if delta.hours > 0:
        pdelta['hours'] = delta.hours
    if delta.minutes > 0:
        pdelta['minutes'] = delta.minutes

    pstr = ''
    for i, k in enumerate(pdelta):
        if i == len(pdelta) - 1:
            pstr = pstr[:-1]
            pstr += f' and {pdelta[k]} {k} ago'
        else:
            pstr += f' {pdelta[k]} {k},'
    return pstr[1:]

def order_by_date(members, member):
    members.sort(key=lambda m: m.created_at)
    rank = str(members.index(member) + 1)
    rint = int(rank[-1])
    if rank[-2] != '1':
        if rint == 0 or rint >= 4:
            suffix = 'th'
        elif rint == 1:
            suffix = 'st'
        elif rint == 2:
            suffix = 'nd'
        elif rint == 3:
            suffix = 'rd'
    else:
        suffix = 'th'
    return f'{rank}{suffix} oldest account on the server'


def to_relativedelta(tdelta):
    return relativedelta(seconds=int(tdelta.total_seconds()), microseconds=tdelta.microseconds)
