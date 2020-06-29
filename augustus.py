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
from cogs.profile import Profile
from mode import token_mode
from mongodb import MongoDB


class Augustus(commands.Bot):
    def __init__(self):
        self.logger = logging.getLogger('discord')
        logging.basicConfig(level=logging.INFO)
        self.db = MongoDB()
        info = json.load(open('info.json'))
        token = info['token'][token_mode()]

        def get_prefix(bot, message):
            if type(message.channel) == discord.TextChannel:
                return bot.db.get_guild(message.guild.id)['prefix']
            else:
                return ['!']

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
        self.add_cog(Profile(self))
        # self.add_cog(Music(self))
        self.run(token)

    async def on_ready(self):
        for guild in self.guilds:
            self.db.add_guild(guild)
            self.db.add_users(guild.members)
        print(f'Logged in as {self.user}')
        print('-----------------------')

    async def on_member_join(self, member):
        self.db.add_member(member)
        self.db.add_user(member.id)
        guild = self.db.get_guild(member.guild.id)
        members = guild['members']
        role_ids = [r for r in members[str(member.id)]['roles'] if r in guild['sticky_roles']]
        if role_ids:
            roles = [member.guild.get_role(rid) for rid in role_ids]
            await member.add_roles(roles)

    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            roles = [r.id for r in after.roles]
            self.db.update_member(after, roles=roles)

    async def on_guild_role_create(self, role):
        self.db.add_role(role)

    async def on_guild_role_delete(self, role):
        self.db.remove_role(role)

    async def on_guild_join(self, guild):
        self.db.add_guild(guild)
        self.db.add_users(guild.members)
    
    async def on_guild_remove(self, guild):
        self.db.remove_guild(guild.id)
    
    