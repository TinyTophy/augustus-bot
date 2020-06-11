from pymongo import MongoClient
import logging
import json
from mode import db_mode
import discord


class db:
    def __init__(self, logger):
        connect = json.load(open('info.json'))['mongo']
        myclient = MongoClient(connect)

        mydb = myclient[db_mode()]
        self.guilds = mydb['guilds']
        self.users = mydb['users']
        self.info = mydb['info']
        self.logger = logger
        if 'prod' in myclient.list_database_names():
            print('Connected to database!')

# Info functions
    def add_info(self):
        self.info.insert_one({'reasons': [
        'Auto-moderation action: spam',
        'Auto-moderation action: banned word'
        ]})

    def get_info(self):
        return self.info.find()[0]

# Guild functions

    def add_guild(self, guild: discord.Guild) -> None:
        prefix = json.load(open('info.json'))['state']
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
            'warn_mute_limit': None,
            'warn_kick_limit': None,
            'warn_ban_limit': None,
            'msg_xp': 5,
            'members': {
                str(m.id): {
                    'roles': [r.id for r in m.roles], 
                    'quotes': [], 
                    'warns': 0, 
                    'xp': 0
                } for m in guild.members
            },
            'roles': [r.id for r in guild.roles],
            'sticky_roles': [],
            'autoroles': [],
            'reaction_roles': {},
            'blacklist': [],
            'modlog_entries': [],
            'votes': [],
            'ranks': {}
        }
        if not self.guilds.find_one({'_id': guild.id}):
            g = self.guilds.insert_one(gdict)
            self.logger.log(level=logging.INFO, msg=f'Added guild {g.inserted_id} to database')

    def add_reaction_role(self, guild_id: int, msg_id: int, rr: dict) -> None:
        update = self.guilds.find_one({'_id': guild_id})

        # If the message is not in the db yet
        if str(msg_id) not in update['reaction_roles']:
            update['reaction_roles'][str(msg_id)] = {'type': 'normal', 'rrs': rr}

        else:
            i = list(rr.keys())[0]
            update['reaction_roles'][str(msg_id)]['rrs'][i] = rr[i]
        self.guilds.update_one({'_id': guild_id}, {'$set': update})
        self.logger.log(level=logging.INFO, msg=f'Added reaction role {rr} to database')

    def add_member(self, guild_id: int, member: discord.Member) -> None:
        update = self.guilds.find_one({'_id': guild_id})
        if str(member.id) not in update['members']:
            update['members'][str(member.id)] = {'verified': False, 'roles': [r.id for r in member.roles]}
            self.guilds.update_one({'_id': guild_id}, {'$set': update})
            self.logger.log(level=logging.INFO, msg=f'Updated guild {guild_id} with {update} in database')

    def add_vote(self, guild_id: int, vote: dict) -> None:
        guild = self.guilds.find_one({'_id': guild_id})
        if guild['votes'] == []:
            guild['votes'] = [vote]
        else:
            guild['votes'].append(vote)
        self.guilds.update_one({'_id': guild_id}, {'$set': guild})
        self.logger.log(level=logging.INFO, msg=f'Added vote {vote} to database')

    def update_guild(self, guild_id: int, update: dict) -> None:
        gid = self.guilds.find({'_id': guild_id})[0]['_id']
        self.guilds.update_one({'_id': guild_id}, {'$set': update})
        self.logger.log(level=logging.INFO, msg=f'Updated guild {gid} with {update} in database')

    def update_rr_type(self, guild_id: int, msg_id: int, update: dict) -> None:
        rrs = self.guilds.find({'_id': guild_id})[0]['reaction_roles']
        rrs[str(msg_id)]['type'] = update
        self.guilds.update_one({'_id': guild_id}, {'$set': {'reaction_roles': rrs}})
        self.logger.log(level=logging.INFO, msg=f'Updated reaction role type for {msg_id} in database')

    def find_guild(self, guild_id: int) -> list:
        return list(self.guilds.find({'_id': guild_id}))[0]

    def find_guild_member(self, guild_id: int, member_id: int) -> dict:
        members = self.guilds.find({'_id': guild_id})[0]['members']
        if str(member_id) in members:
            return members[str(member_id)]

    def all_guilds(self) -> list:
        return list(self.guilds.find())

    def delete_guild(self, guild_id: int) -> None:
        self.guilds.delete_one({'_id': guild_id})
        self.logger.log(level=logging.INFO, msg=f'Deleted guild {guild_id} in database')

    def delete_vote(self, guild_id: int, vote: dict):
        guild = self.guilds.find_one({'_id': guild_id})
        guild['votes'].remove(vote)
        self.guilds.update_one({'_id': guild_id}, {'$set': guild})
        self.logger.log(level=logging.INFO, msg=f'Deleted vote {vote} in database')

# User functions

    def add_user(self, user_id: int) -> None:
        if not self.users.find_one({'_id': user_id}):
            user = {'_id': user_id, 'version': 'NRSV'}
            self.users.insert_one(user)
            self.logger.log(level=logging.INFO, msg=f'Added user {user_id} to database')
    
    def add_users(self, users: list) -> None:
        user_ids = [u['_id'] for u in self.users.find()]
        users = [{'_id': u.id, 'version': 'NRSV'} for u in users if u.id not in user_ids]
        if not users:
            return
        self.users.insert_many(users)
        self.logger.log(level=logging.INFO, msg=f'Added new users to database')

    def update_user(self, user_id: int, update: dict) -> None:
        self.users.update_one({'_id': user_id}, {'$set': update}) 
        self.logger.log(level=logging.INFO, msg=f'Updated user {user_id} to database')
    
    def find_user(self, user_id: int) -> dict:
        return self.users.find_one({'_id': user_id})