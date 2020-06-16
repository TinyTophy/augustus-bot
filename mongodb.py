from pymongo import MongoClient
import logging
import json
from mode import db_mode
import discord
from bson.objectid import ObjectId


class MongoDB(MongoClient):
    def __init__(self, logger=None):
        myclient = MongoClient(json.load(open('info.json'))['mongo'])

        mydb = myclient[db_mode()]
        self.guilds = mydb['guilds']
        self.users = mydb['users']
        self.info = mydb['info']
        self.logger = logger
        self.guilds.create_index('members.member-id', unique=True)
        if 'prod' in myclient.list_database_names():
            print('Connected to database!')


# Guild Functions

    # Create Function
    def add_guild(self, guild: discord.Guild) -> None:
        prefix = json.load(open('info.json'))['state']
        if not self.guilds.find_one({'_id': guild.id}):
            self.guilds.insert_one(
                {
                    '_id': guild.id,
                    'prefix': [prefix, '.'],
                    'muterole_id': None,
                    'modrole_id': None,
                    'modmail_channel_id': None,
                    'modlog_channel_id': None,
                    'log_channel_id': None,
                    'verify_role_id': None,
                    'verify_log_channel_id': None,
                    'warn_mute_limit': None,
                    'warn_kick_limit': None,
                    'warn_ban_limit': None,
                    'msg_xp': 5,
                    'members': [
                        {
                            'member_id': m.id,
                            'roles': [r.id for r in m.roles], 
                            'quotes': [], 
                            'warns': 0, 
                            'xp': 0
                        } for m in guild.members
                    ],
                    'roles': [r.id for r in guild.roles],
                    'sticky_roles': [],
                    'autoroles': [],
                    'reaction_roles': [],
                    'modlog_entries': [],
                    'ranks': [],
                    'level_msg': True
                }
            )
            self.logger.log(
                level=logging.INFO, 
                msg=f'Added guild {guild.id} to database'
            )

    # Read Functions
    def get_guild(self, guild_id: int) -> dict:
        return self.guilds.find_one(
            {
                '_id': guild_id
            }
        )
    
    def get_all_guilds(self) -> list:
        return list(self.guilds.find())

    # Update Function
    def update_guild(self, guild_id: int, **kwargs) -> None:
        self.guilds.update_one(
            {'_id': guild_id}, 
            {'$set': {
                k:kwargs[k] for k in kwargs
                }
            }
        )
        self.logger.log(
            level=logging.INFO, 
            msg=f'Updated guild {guild_id} in database'
        )
    
    # Delete Function
    def remove_guild(self, guild_id: int) -> None:
        self.guilds.delete_one(
            {
                '_id': guild_id
            }
        )
        self.logger.log(
            level=logging.INFO, 
            msg=f'Deleted guild {guild_id} in database'
        )


# Member Functions
    
    # Create Function
    def add_member(self, guild_id: int, member: discord.Member) -> None:
        update = self.guilds.find_one({'_id': guild_id})
        if member.id not in update['members']:
            self.guilds.update_one(
                {
                    '_id': guild_id
                },
                {'$set': {
                    f'members.{member.id}': {
                        'verified': False, 'roles': [r.id for r in member.roles]
                        }
                    }
                }
            )
            self.logger.log(
                level=logging.INFO,
                msg=f'Updated guild {guild_id} with {update} in database'
            )
    
    # Read Functions
    def get_member(self, member: discord.Member) -> dict:
        return self.guilds.find_one(
            {'_id': member.guild.id},
            {
                'members': {
                    '$elemMatch': {
                        '_id': member.id
                    }
                }
            }
        )['members'][0]
    
    def get_all_members(self, guild_id: int) -> list:
        return self.guilds.find_one({'_id': guild_id})['members']

    def update_member(self, member: discord.Member, **kwargs) -> None:
        self.guilds.update_one(
            {
                '_id': member.guild.id
            }, 
            {'$set': {
                f'members.$.{member.id}.{k}': kwargs[k] for k in kwargs
                }
            }
        )
        self.logger.log(
            level=logging.INFO, 
            msg=f'Updated member {member.id} in {member.guild.id} in database'
        )


# Role Functions

    # Create Function
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
    
    # Delete Function
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

    # Create Function
    def add_rr(self, guild_id: int, msg_id: int, rr: dict) -> None:
        update = self.guilds.find_one(
            {
                '_id': guild_id
            }
        )

        # If the message is not in the db yet
        if str(msg_id) not in update['reaction_roles']:
            update['reaction_roles'][str(msg_id)] = {'type': 'normal', 'rrs': rr}

        else:
            i = list(rr.keys())[0]
            update['reaction_roles'][str(msg_id)]['rrs'][i] = rr[i]
        self.guilds.update_one({'_id': guild_id}, {'$set': update})
        self.logger.log(level=logging.INFO, msg=f'Added reaction role {rr} to database')
    
    # Update Function
    def update_rr(self, guild_id: int, msg_id: int, update: dict) -> None:
        rrs = self.guilds.find_one({'_id': guild_id})['reaction_roles']
        rrs[str(msg_id)]['type'] = update
        self.guilds.update_one({'_id': guild_id}, {'$set': {'reaction_roles': rrs}})
        self.logger.log(level=logging.INFO, msg=f'Updated reaction role type for {msg_id} in database')


# Rank Functions

    def add_rank(self, guild_id: int, role: discord.Role, level: int) -> None:
        guild = self.guilds.find_one({'_id': guild_id})
        if str(role.id) not in guild['ranks']:
            self.guilds.update_one({'_id': guild_id}, {'$set': {f'ranks.{role.id}': level}})
            self.logger.log(level=logging.INFO, msg=f'Added rank for {role.id} for {guild_id} in database')
    
    def delete_rank(self, guild_id: int, role_id: int) -> None:
        guild = self.guilds.find_one({'_id': guild_id})
        if str(role_id) in guild['ranks']:
            self.guilds.update_one({'_id': guild_id}, {'$unset': {'ranks': str(role_id)}})
            self.logger.log(level=logging.INFO, msg=f'Removed rank for {role_id} for {guild_id} in database')

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
                msg=f'Added user {user_id} to database'
            )
    
    def add_users(self, users: list) -> None:
        user_ids = [u['_id'] for u in self.users.find()]
        users = [{'_id': u.id, 'version': 'NRSV'} for u in users if u.id not in user_ids]
        if not users:
            return
        self.users.insert_many(users)
        self.logger.log(level=logging.INFO, msg=f'Added new users to database')

    def update_user(self, user_id: int, update: dict) -> None:
        self.users.update_one(
            {'_id': user_id}, 
            {'$set': update}
        ) 
        self.logger.log(
            level=logging.INFO, 
            msg=f'Updated user {user_id} to database'
        )
    
    def find_user(self, user_id: int) -> dict:
        return self.users.find_one({'_id': user_id})