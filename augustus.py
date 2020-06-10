import json
import logging

import discord
from discord.ext import commands

from cogs.bible import Bible
from cogs.embed import Embed
from cogs.help import Help
from cogs.latex import Latex
from cogs.levels import Levels
from cogs.log import Log
from cogs.misc import Misc
from cogs.mod import Mod
from cogs.modlog import ModLog
from cogs.modmail import Modmail
from cogs.music import Music
from cogs.quickpoll import Quickpoll
from cogs.quotes import Quotes
from cogs.reactionrole import ReactionRole
from cogs.vote import Vote
from mode import token_mode
from mongodb import db
from utils import get_prefix


class Augustus(commands.Bot):
    def __init__(self):
        self.logger = logging.getLogger('discord')
        logging.basicConfig(level=logging.INFO)
        self.db = db(self.logger)
        info = json.load(open('info.json'))
        token = info['token'][token_mode()]
        super().__init__(command_prefix=get_prefix, help_command=Help())
        self.add_cog(Bible(self))
        self.add_cog(Modmail(self))
        self.add_cog(ModLog(self))
        self.add_cog(Mod(self))
        self.add_cog(Misc(self))
        self.add_cog(Quickpoll(self))
        self.add_cog(Quotes(self))
        self.add_cog(Embed(self))
        self.add_cog(ReactionRole(self))
        self.add_cog(Levels(self))
        self.add_cog(Music(self))
        self.run(token)

    async def on_ready(self):
        for guild in self.guilds:
            self.db.add_guild(guild)
        await self.change_presence(activity=discord.Game(name=f'DM me for staff'))
        print(f'Logged in as {self.user}')
        print('-----------------------')
    
    async def on_member_join(self, member):
        self.db.add_member(member.guild.id, member)
        guild = self.db.find_guild(member.guild.id)[0]
        members = guild['members']
        role_ids = [r for r in members[str(member.id)]['roles'] if r in guild['sticky_roles']]
        if role_ids != []:
            roles = [member.guild.get_role(rid) for rid in role_ids]
            await member.add_roles(roles)

    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            update = self.db.find_guild(before.guild.id)[0]
            update['members'][str(before.id)]['roles'] = [r.id for r in after.roles]
            self.db.update_guild(before.guild.id, update)
    
    async def on_guild_remove(self, guild):
        self.db.delete_guild(guild.id)

    async def on_guild_role_create(self, role):
        roles = self.db.find_guild(role.guild.id)[0]['roles']
        roles.append(role.id)
        self.db.update_guild(role.guild.id, {'roles': roles})

    async def on_guild_role_delete(self, role):
        roles = self.db.find_guild(role.guild.id)[0]['roles']
        roles.remove(role.id)
        self.db.update_guild(role.guild.id, {'roles': roles})
    
    # On member join checks database for records on member.
    # If it finds pre-existing data, it adds roles that are set to sticky.
    # If no data is found it will add member to database.
    async def on_guild_join(self, guild):
        prefix = json.load(open('info.json'))['state']
        self.db.add_guild(guild)
