from discord.ext import commands
import discord
from dateutil.relativedelta import relativedelta
import json


def is_staff():
    def predicate(ctx):
        modrole = ctx.guild.get_role(ctx.cog.db.find_guild(
            {'_id': ctx.guild.id})[0]['modrole_id'])
        return modrole in ctx.author.roles or ctx.author.guild_permissions.administrator
    return commands.check(predicate)

def not_staff(modrole, target):
    return modrole not in target.roles and not target.guild_permissions.administrator

def is_admin(member):
    return member.guild_permissions.administrator

def is_muted(member, muterole):
    return muterole in member.roles

def load_guilds(db, guilds):
    prefix = json.load(open('info.json'))['state']
    for guild in guilds:
        gdict = {
            '_id': guild.id,
            'prefix': [prefix, '.'],
            'muterole_id': None,
            'modrole_id': None,
            'modmail_channel_id': None,
            'modlog_channel_id': None,
            'log_channel_id': None,
            'verify_role_id': None,
            'verify_log_channel_id': None,
            'autoclose_votes': False,
            'members': {str(m.id): {'verified': False, 'roles': [r.id for r in m.roles], 'quotes': []} for m in guild.members},
            'roles': [r.id for r in guild.roles],
            'sticky_roles': [],
            'autoroles': [],
            'reaction_roles': {},
            'blacklist': [],
            'modlog_entries': [],
            'votes': []
        }
        old = list(db.find_guild({'_id': guild.id}))

        # If the old guild doesn't exist in the db then add all data
        if old == []:
            db.add_guild(gdict)

        # Else if guild does exist in the db and is different than current discord data, then update db
        elif {k: gdict[k] for k in gdict if k in old[0] and gdict[k] != old[0][k]} != {}:
            for m in gdict['members']:
                members = old[0]['members']
                if m in members and members[m]['verified'] == True:
                    gdict['members'][m]['verified'] = True
                update = {k: gdict[k] for k in gdict if k in old[0] and gdict[k] != old[0][k]}

            # Set all server preferences to what they were before
            update['prefix'] = old[0]['prefix']
            update['muterole_id'] = old[0]['muterole_id']
            update['modrole_id'] = old[0]['modrole_id']
            update['modmail_channel_id'] = old[0]['modmail_channel_id']
            update['modlog_channel_id'] = old[0]['modlog_channel_id']
            update['log_channel_id'] = old[0]['log_channel_id']
            update['verify_role_id'] = old[0]['verify_role_id']
            update['verify_log_channel_id'] = old[0]['verify_log_channel_id']
            if 'autoclose_votes' in old[0]:
                update['autoclose_votes'] = old[0]['autoclose_votes']
            else:
                update['autoclose_votes'] = False
            update['sticky_roles'] = old[0]['sticky_roles']
            update['autoroles'] = old[0]['autoroles']
            update['reaction_roles'] = old[0]['reaction_roles']
            update['blacklist'] = old[0]['blacklist']
            update['modlog_entries'] = old[0]['modlog_entries']
            update['votes'] = old[0]['votes']

            db.update_guild({'_id': guild.id}, update)

def get_prefix(bot, message):
    try:
        return bot.db.find_guild({'_id': message.guild.id})[0]['prefix']
    except Exception as e:
        print(e)

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
