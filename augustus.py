import json
import logging

import discord
from discord.ext import commands

from mongodb import MongoDB


class Augustus(commands.Bot):
    def __init__(self, token, db, helpcog, *cogs):
        self.logger = logging.getLogger('discord')
        logging.basicConfig(level=logging.INFO)
        self.db = db
        super().__init__(
            command_prefix=lambda bot, message: bot.db.get_guild(message.guild.id)['prefixes'],
            help_command=helpcog()
        )
        for cog in cogs:
            self.add_cog(cog(self))

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
