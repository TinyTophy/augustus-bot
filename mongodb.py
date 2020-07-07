from pymongo import MongoClient
import logging
from mode import db_mode
import discord
import os


class MongoDB():
    def __init__(self, logger=None):
        client = MongoClient(os.environ['MONGO'])
        self.prefix = db_mode()
        mydb = client[self.prefix]
        self.guilds = mydb['guilds']
        self.users = mydb['users']
        self.bibles = mydb['bibles']
        if not logger:
            self.logger = logging.getLogger('database')
            logging.basicConfig(level=logging.INFO)

# Guild Functions

    def add_guild(self, guild: discord.Guild) -> None:
        global prefix
        if self.prefix == 'prod':
            prefix = ':aug: '
        elif self.prefix == 'dev':
            prefix = ':dev: '

        if not self.guilds.find_one({'_id': guild.id}):
            self.guilds.insert_one(
                {
                    '_id': guild.id,
                    'prefixes': [prefix, '.'],
                    'muterole_id': None,
                    'role_perms': None,
                    'modlog_channel_id': None,
                    'log_channel_id': None,
                    'verify_role_id': None,
                    'verify_log_channel_id': None,
                    'warn_mute_limit': None,
                    'warn_kick_limit': None,
                    'warn_ban_limit': None,
                    'msg_xp': None,
                    'level_msg': True,
                    'members': [
                        {
                            'id': m.id,
                            'display_name': f'{m.name}#{m.discriminator}',
                            'roles': [r.id for r in m.roles],
                            'quotes': [],
                            'warns': 0,
                            'xp': 0
                        }
                        for m in guild.members],
                    'help_channels': [],
                    'roles': [r.id for r in guild.roles],
                    'sticky_roles': [],
                    'autoroles': [],
                    'reaction_roles': [],
                    'modlog_entries': [],
                    'ranks': []
                }
            )
            self.logger.log(
                level=logging.INFO,
                msg=f'Added guild {guild.id}'
            )

    def get_guild(self, guild_id: int) -> dict:
        return self.guilds.find_one(
            {
                '_id': guild_id
            }
        )

    def get_all_guilds(self) -> list:
        return list(self.guilds.find())

    def update_guild(self, guild_id: int, **kwargs) -> None:
        self.guilds.update_one(
            {'_id': guild_id},
            {'$set': {
                k: kwargs[k] for k in kwargs
                }
            }
        )
        self.logger.log(
            level=logging.INFO,
            msg=f'Updated guild {guild_id}'
        )

    def remove_guild(self, guild_id: int) -> None:
        self.guilds.delete_one(
            {
                '_id': guild_id
            }
        )
        self.logger.log(
            level=logging.INFO,
            msg=f'Deleted guild {guild_id}'
        )

# Member Functions

    def add_member(self, member: discord.Member) -> None:
        self.guilds.update_one(
            {
                '_id': member.guild.id
            },
            {'$addToSet': {
                'members': {
                    'id': member.id,
                    'display_name': f'{member.name}#{member.discriminator}',
                    'roles': [r.id for r in member.roles],
                    'quotes': [],
                    'warns': 0,
                    'xp': 0
                    }
                }
            }    
        )
        self.logger.log(
            level=logging.INFO,
            msg=f'Added member {member.id} in {member.guild.id}'
        )

    def get_member(self, member: discord.Member) -> dict:
        try:
            return self.guilds.find_one(
                {
                    '_id': member.guild.id, 
                    'members.id': member.id
                },
                {
                    'members.$': 1
                }
            )['members'][0]
        except Exception as e:
            return e


    def get_all_members(self, guild_id: int) -> list:
        return self.guilds.find_one({'_id': guild_id})['members']

    def update_member(self, member: discord.Member, **kwargs) -> None:
        self.guilds.update_one(
            {
                'members.id': member.id
            },
            {'$set': {
                f'members.$.{k}': kwargs[k] for k in kwargs
                } 
            }
        )
        self.logger.log(
            level=logging.INFO,
            msg=f'Updated member {member.id} in {member.guild.id}'
        )

# Help Channels

    def add_help_channel(self, channel: discord.TextChannel, **kwargs):
        self.guilds.update_one(
            {'_id': channel.guild.id},
            {}
        )

# Role Functions

    def add_role(self, role: discord.Role):
        self.guilds.update_one(
            {'_id': role.guild.id},
            {'$addToSet': {
                'roles': role.id
            }
            }
        )
        self.logger.log(
            level=logging.INFO,
            msg=f'Added role {role.id} for guild {role.guild.id}'
        )

    def remove_role(self, role: discord.Role):
        self.guilds.update_one(
            {'_id': role.guild.id},
            {'$pull': {
                'roles': role.id
            }
            }
        )
        self.logger.log(
            level=logging.INFO,
            msg=f'Removed role {role.id} from guild {role.guild.id}'
        )

# Reaction Role Functions

    def add_rr(self, guild_id: int, msg_id: int, rr: dict) -> None:
        rr_messages = self.guilds.find_one(
            {
                '_id': guild_id
            }
        )['rr_messages']

        if str(msg_id) not in rr_messages:
            self.guilds.update_one(
                {'_id': guild_id},
                {'$set': {
                    f'rr_messages.{msg_id}': {'type': 'normal', 'reaction_roles': rr}
                }
                }
            )

        else:
            self.guilds.update_one(
                {'_id': guild_id},
                {'$set': {
                    f'rr_messages.{msg_id}.reaction_roles.{k}': rr[k]
                } for k in rr
                }
            )
        self.logger.log(
            level=logging.INFO,
            msg=f'Added reaction role {rr}'
        )

    def update_rr(self, guild_id: int, msg_id: int, **kwargs) -> None:
        rr_messages = self.guilds.find_one(
            {
                '_id': guild_id
            }
        )['rr_messages']

        if str(msg_id) not in rr_messages:
            return

        self.guilds.update_one(
            {'_id': guild_id},
            {'$set': {
                f'rr_messages.{msg_id}.{k}': kwargs[k]
            } for k in kwargs
            }
        )
        self.logger.log(
            level=logging.INFO,
            msg=f'Updated reaction role type for {msg_id}'
        )

    def remove_rr(self, guild_id: int, msg_id: int):
        self.guilds.update_one(
            {'_id': guild_id},
            {'$unset': {
                f'rr_messages.{msg_id}': ''
            }
            }
        )
        self.logger.log(
            level=logging.INFO,
            msg=f'Removed reaction role for {msg_id} in {guild_id}'
        )

# Rank Functions

    def add_rank(self, guild_id: int, role: discord.Role, level: int) -> None:
        guild = self.guilds.find_one({'_id': guild_id})
        if str(role.id) not in guild['ranks']:
            self.guilds.update_one({'_id': guild_id}, {'$set': {f'ranks.{role.id}': level}})
            self.logger.log(
                level=logging.INFO,
                msg=f'Added rank for {role.id} for {guild_id}'
            )

    def delete_rank(self, guild_id: int, role_id: int) -> None:
        guild = self.guilds.find_one({'_id': guild_id})
        if str(role_id) in guild['ranks']:
            self.guilds.update_one({'_id': guild_id}, {'$unset': {'ranks': str(role_id)}})
            self.logger.log(
                level=logging.INFO,
                msg=f'Removed rank for {role_id} for {guild_id}'
            )

# User Functions

    def add_user(self, user_id: int) -> None:
        if not self.users.find_one({'_id': user_id}):
            self.users.insert_one(
                {
                    '_id': user_id,
                    'version': 'NRSV'
                }
            )
            self.logger.log(
                level=logging.INFO,
                msg=f'Added user {user_id}'
            )

    def add_users(self, users: list) -> None:
        user_ids = [u['_id'] for u in self.users.find()]
        users = [{'_id': u.id, 'version': 'NRSV'} for u in users if u.id not in user_ids]
        if not users:
            return
        self.users.insert_many(users)
        self.logger.log(
            level=logging.INFO,
            msg=f'Added new users'
        )

    def update_user(self, user_id: int, **kwargs) -> None:
        self.users.update_one(
            {'_id': user_id},
            {'$set': {
                k: kwargs[k] for k in kwargs
            }
            }
        )
        self.logger.log(
            level=logging.INFO,
            msg=f'Updated user {user_id}'
        )

    def find_user(self, user_id: int) -> dict:
        return self.users.find_one({'_id': user_id})
