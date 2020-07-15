import logging
import os

import discord
from pymongo import MongoClient

from mode import db_mode
from models.guild import Guild
from models.member import Member
from models.role import Role
from models.user import User


class MongoDB():
    def __init__(self, bot, logger=None):
        client = MongoClient(os.environ['MONGO'])
        self.mode = db_mode()
        self.bot = bot
        mydb = client[self.mode]
        self.guilds = mydb['guilds']
        self.users = mydb['users']
        self.bibles = mydb['bibles']
        if not logger:
            self.logger = logging.getLogger('database')
            logging.basicConfig(level=logging.INFO)

# Guild Functions

    def add_guild(self, guild: discord.Guild) -> None:
        try:
            self.guilds.insert_one(guild.__dict__)
            self.logger.log(
                level=logging.INFO,
                msg=f'Added guild {guild.id}'
            )
        except:
            return None

    def get_guild(self, guild_id: int) -> dict:
        return Guild(self.bot, **self.guilds.find_one(
                {
                    '_id': guild_id
                }
            )
        )

    def get_all_guilds(self) -> list:
        return [Guild(self.bot, **g) for g in self.guilds.find()]

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

    def add_member(self, member: Member) -> None:
        if self.guilds.get_member(member.id):
            return

        self.guilds.update_one(
            {
                '_id': member.guild.id
            },
            {'$addToSet': {
                'members': member
                }
            }    
        )
        self.logger.log(
            level=logging.INFO,
            msg=f'Added member {member.id} in {member.guild.id}'
        )

    def get_member(self, member: discord.Member) -> dict:
        return Member(self.bot, **self.guilds.find_one(
            {
                '_id': member.guild.id, 
                'members.id': member.id
            },
            {
                'members.$': 1
            }
        )['members'][0])

    def get_all_members(self, guild_id: int) -> list:
        return [Member(self.bot, **m) for m in self.guilds.find_one({'_id': guild_id})['members']]

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

    def add_role(self, role: Role):
        self.guilds.update_one(
            {'_id': role.guild.id},
                {'$addToSet': {
                    'roles': role
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
                    'roles': {'id': role.id}
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
        rank = {'role_id': role.id, 'level': level}
        self.guilds.update_one({'_id': guild_id}, {'$addToSet': {'ranks': rank}})
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

    def add_user(self, user: User) -> None:
        try:
            self.users.insert_one(user.__dict__)
            self.logger.log(
                level=logging.INFO,
                msg=f'Added user {user.id}'
            )
        except Exception as e:
            return e

    def add_users(self, users: list) -> None:
        # user_ids = [u['_id'] for u in self.users.find()]
        # users = [u for u in users if u.id not in user_ids]
        # if not users:
        #     return
        self.users.insert_many([u.__dict__ for u in users])
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

    def get_user(self, user_id: int) -> dict:
        user = self.users.find_one({'_id': user_id})
        if user:
            return User(self.bot, **user)
        else:
            return None
