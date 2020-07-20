import logging

import discord
from discord.ext import commands
from models.user import User
from models.guild import Guild


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        self.logger = logging.getLogger('discord')
        logging.basicConfig(level=logging.INFO)
        self.db = kwargs['db'](self)
        if 'help' not in kwargs:
            help = commands.DefaultHelpCommand
        else:
            help = kwargs['help']
        super().__init__(
            command_prefix=lambda bot, message: bot.db.get_guild(message.guild.id).prefixes,
            help_command=help()
        )
        if 'cogs' in kwargs:
            for cog in kwargs['cogs']:
                self.add_cog(cog(self))

        self.run(kwargs['token'])

    async def on_ready(self):
        for guild in self.guilds:
            self.db.add_guild(Guild(self, guild, False))
            self.db.add_users([User(self, u, False) for u in guild.members])
        
        print(f'Logged in as {self.user}')
        print('-----------------------')

    async def on_member_join(self, member):
        self.db.add_member(member)
        self.db.add_user(member.id)
        sticky_roles = self.db.get_guild(member.guild.id)['sticky_roles']
        member_roles = self.db.get_member(member)['roles']
        roles = [member.guild.get_role(r) for r in member_roles if r in sticky_roles]
        if roles:
            await member.add_roles(*roles)

    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            self.db.update_member(after, roles=[r.id for r in after.roles])

    async def on_guild_role_create(self, role):
        self.db.add_role(role)

    async def on_guild_role_delete(self, role):
        self.db.remove_role(role)

    async def on_guild_join(self, guild):
        self.db.add_guild(guild)
        self.db.add_users(guild.members)

    async def on_guild_remove(self, guild):
        self.db.remove_guild(guild.id)