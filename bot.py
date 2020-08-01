import logging

import discord
from discord.ext import commands


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        self.prefixes = {}
        self.logger = logging.getLogger('discord')
        logging.basicConfig(level=logging.INFO)
        self.db = kwargs['db']
        if 'help' not in kwargs:
            help = commands.DefaultHelpCommand
        else:
            help = kwargs['help']
        super().__init__(
            command_prefix=self.get_prefixes,
            help_command=help()
        )
        if 'cogs' in kwargs:
            for cog in kwargs['cogs']:
                self.add_cog(cog(self))
        self.loop.create_task(self.startup())
    
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print('-----------------------')
    
    def get_prefixes(self, bot, message):
        return self.prefixes[str(message.guild.id)]

    async def set_prefixes(self, guild_id):
        self.prefixes[str(guild_id)] = await self.db.get_guild_prefixes(guild_id)
    
    async def startup(self):
        await self.wait_until_ready()
        await self.db.run()
        tr = await self.db.begin_trans()
        try:
            version_id = await self.db.add_bible_version('nrsv')
        except:
            await tr.rollback()
            raise
        else:
            await tr.commit()
        if not version_id:
            version_id = await self.db.get_bible_version_id('nrsv')
        for g in self.guilds:
            tr = await self.db.begin_trans()
            try:
                await self.db.add_guild(g.id, 5, False, None, None)
                await self.db.add_guild_roles([(str(r.id), str(g.id), False, False) for r in g.roles])
                await self.db.add_users([(str(u.id), version_id) for u in g.members])
                await self.db.add_guild_members([(str(m.id), str(g.id), 0, 0) for m in g.members])
                await self.db.add_guild_prefix(g.id, '$')
            except:
                await tr.rollback()
                raise
            else:
                await tr.commit()
            
        for g in self.guilds:
            await self.set_prefixes(g.id)

    # async def on_member_join(self, member):
    #     self.db.add_member(member)
    #     self.db.add_user(member.id)
    #     sticky_roles = self.db.get_guild(member.guild.id)['sticky_roles']
    #     member_roles = self.db.get_member(member)['roles']
    #     roles = [member.guild.get_role(r) for r in member_roles if r in sticky_roles]
    #     if roles:
    #         await member.add_roles(*roles)

    # async def on_member_update(self, before, after):
    #     if before.roles != after.roles:
    #         self.db.update_member(after, roles=[r.id for r in after.roles])

    # async def on_guild_role_create(self, role):
    #     self.db.add_role(role)

    # async def on_guild_role_delete(self, role):
    #     self.db.remove_role(role)

    # async def on_guild_join(self, guild):
    #     self.db.add_guild(guild)
    #     self.db.add_users(guild.members)

    # async def on_guild_remove(self, guild):
    #     self.db.remove_guild(guild.id)
