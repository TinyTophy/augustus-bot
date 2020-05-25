import pymongo
import logging
import json
from mode import db_mode


class db:
    def __init__(self, logger):
        username = json.load(open('info.json'))['mongo']['username']
        password = json.load(open('info.json'))['mongo']['password']
        cluster = json.load(open('info.json'))['mongo']['cluster']
        myclient = pymongo.MongoClient(
            f'mongodb+srv://{username}:{password}@{cluster}.mongodb.net/test?retryWrites=true&w=majority')

        mydb = myclient[db_mode()]
        self.guilds = mydb['guilds']
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

    def add_guild(self, guild):
        g = self.guilds.insert_one(guild)
        self.logger.log(level=logging.INFO,
                        msg=f'Added guild {g.inserted_id} to database')

    def add_reaction_role(self, query, msg_id, rr):
        update = self.guilds.find_one(query)

        # If the message is not in the db yet
        if str(msg_id) not in update['reaction_roles']:
            update['reaction_roles'][str(msg_id)] = {'type': 'normal', 'rrs': rr}

        else:
            i = list(rr.keys())[0]
            update['reaction_roles'][str(msg_id)]['rrs'][i] = rr[i]
        self.guilds.update_one(query, {'$set': update})
        self.logger.log(level=logging.INFO,
                        msg=f'Added reaction role {rr} to database')

    def add_member(self, guild_id, member):
        update = self.guilds.find_one({'_id': guild_id})
        if str(member.id) not in update['members']:
            update['members'][str(member.id)] = {'verified': False, 'roles': [r.id for r in member.roles]}
            self.guilds.update_one({'_id': guild_id}, {'$set': update})
            self.logger.log(level=logging.INFO,
                            msg=f'Updated guild {guild_id} with {update} in database')

    def add_vote(self, guild_id, vote):
        guild = self.guilds.find_one({'_id': guild_id})
        if guild['votes'] == []:
            guild['votes'] = [vote]
        else:
            guild['votes'].append(vote)
        self.guilds.update_one({'_id': guild_id}, {'$set': guild})
        self.logger.log(level=logging.INFO,
                        msg=f'Added vote {vote} to database')

    def update_guild(self, query, update):
        gid = self.guilds.find(query)[0]['_id']
        self.guilds.update_one(query, {'$set': update})
        self.logger.log(level=logging.INFO,
                        msg=f'Updated guild {gid} with {update} in database')

    def update_rr_type(self, query, msg_id, update):
        rrs = self.guilds.find(query)[0]['reaction_roles']
        rrs[str(msg_id)]['type'] = update
        self.guilds.update_one(query, {'$set': {'reaction_roles': rrs}})
        self.logger.log(level=logging.INFO,
                        msg=f'Updated reaction role type for {msg_id} in database')

    def find_guild(self, query):
        return self.guilds.find(query)

    def find_guild_member(self, query, member_id):
        members = self.guilds.find(query)[0]['members']
        if str(member_id) in members:
            return members[str(member_id)]

    def all_guilds(self):
        return self.guilds.find()

    def delete_guild(self, query):
        gid = self.guilds.find(query)[0]['_id']
        self.guilds.delete_one(query)
        self.logger.log(level=logging.INFO,
                        msg=f'Deleted guild {gid} in database')

    def delete_vote(self, guild_id, vote):
        guild = self.guilds.find_one({'_id': guild_id})
        guild['votes'].remove(vote)
        self.guilds.update_one({'_id': guild_id}, {'$set': guild})
        self.logger.log(level=logging.INFO,
                        msg=f'Deleted vote {vote} in database')
