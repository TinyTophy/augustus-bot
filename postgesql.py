import psycopg2
import json
from mode import db_mode
import logging


class db:
    def __init__(self, logger):
        info = json.load(open('info.json'))['postgresql']
        self.logger = logger
        self.conn = psycopg2.connect(
            host=info['host'],
            database=db_mode(),
            user=info['user'],
            password=info['password']
        )
        self.cur = self.conn.cursor()
        self.cur.execute(open('schema.sql', 'r').read())

    # Add Functions
    def add_guild(self, guild_id):
        self.cur.execute(
            "INSERT INTO Guild (id) VALUES (%s) ON CONFLICT DO NOTHING", [guild_id])
        self.conn.commit()
        self.logger.log(level=logging.INFO,
                        msg=f'Added guild {guild_id} to database')

    def add_member(self, member):
        self.cur.execute(
            'INSERT OR IGNORE INTO Member VALUES (%s) ON CONFLICT DO NOTHING', [member.id])
        self.conn.commit()
        self.logger.log(level=logging.INFO,
                        msg=f'Added member {member.id} to database')

    def add_role(self, role):
        self.cur.execute(
            'INSERT OR IGNORE INTO Discord_Role VALUES (%s, %s) ON CONFLICT DO NOTHING', (role.id, role.guild.id))
        self.conn.commit()
        self.logger.log(level=logging.INFO,
                        msg=f'Added role {role.id} to database')

    def add_modlog_entry(self, entry):
        self.cur.execute(
            'SELECT COUNT(*) FROM Modlog_Entry WHERE guild_id=%s', (entry['guild_id'],))
        case = dict(self.cur.fetchone())['COUNT(*)'] + 1
        if entry['reason'] == '':
            entry['reason'] = f'No reason given, use `!reason {case} <reason>` to add one'
        self.cur.execute('INSERT INTO Modlog_Entry (case_id, guild_id, modlog_id, mod_type, reason) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING',
                         (case, entry['guild_id'], entry['modlog_id'], entry['mod_type'], entry['reason']))
        self.conn.commit()
        self.logger.log(
            level=logging.INFO, msg=f'''Added entry {entry['guild_id']}:{case} in database''')
        return case

    def add_reaction_role(self, guild_id, role_id, msg_id, reaction):
        self.cur.execute('INSERT OR IGNORE INTO Reaction_Role (guild_id, role_id, message_id, reaction) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING',
                         (guild_id, role_id, msg_id, reaction))
        self.conn.commit()
        self.cur.execute('SELECT id FROM Reaction_Role WHERE guild_id=%s AND role_id=%s AND message_id=%s AND reaction=%s',
                         (guild_id, role_id, msg_id, reaction))
        case_id = self.cur.fetchone()['id']
        self.logger.log(level=logging.INFO,
                        msg=f'Added reaction role {case_id}')

    # Update Functions
    def update_guild(self, guild_id, **kwargs):
        cols = ','.join([f'{key}=%s' for key in kwargs.keys()])
        try:
            if kwargs['modmail_channel_id'] == '':
                self.cur.execute(
                    f'UPDATE Guild SET modmail_channel_id=null WHERE guild_id=%s', (guild_id,))
            else:
                self.cur.execute(
                    f'UPDATE Guild SET {cols} WHERE guild_id=%s', (*kwargs.values(), guild_id))
        except Exception as e:
            self.cur.execute(
                f'UPDATE Guild SET {cols} WHERE guild_id=%s', (*kwargs.values(), guild_id))

        self.conn.commit()
        self.logger.log(level=logging.INFO,
                        msg=f'Updated guild {guild_id} in database')

    def update_modlog_entry(self, case_id, guild_id, **kwargs):
        cols = ','.join([f'{key}=%s' for key in kwargs.keys()])
        self.cur.execute(f'UPDATE Modlog_Entry SET {cols} WHERE case_id=%s AND guild_id=%s', (
            *kwargs.values(), case_id, guild_id))
        self.conn.commit()
        self.logger.log(level=logging.INFO,
                        msg=f'Updated entry {guild_id}:{case_id} in database')

    def update_rr(self, case_id, status):
        self.cur.execute(
            'UPDATE Reaction_Role SET status=%s WHERE id=%s', (status, case_id))
        self.conn.commit()
        self.logger.log(level=logging.INFO,
                        msg=f'Updated reaction role {case_id} in database')

    # Remove Functions
    def remove_guild(self, guild_id):
        self.cur.execute('DELETE FROM Guild WHERE guild_id=%s', guild_id)
        self.conn.commit()
        self.logger.log(level=logging.INFO,
                        msg=f'Removed guild {guild_id} from database')

    def remove_member(self, member_id):
        self.cur.execute('DELETE FROM Member WHERE discord_id=%s', member_id)
        self.conn.commit()
        self.logger.log(level=logging.INFO,
                        msg=f'Removed member {member_id} from database')

    def remove_role(self, role_id):
        self.cur.execute('DELETE FROM Discord_Role WHERE role_id=%s', role_id)
        self.conn.commit()
        self.logger.log(level=logging.INFO,
                        msg=f'Removed role {role_id} from database')

    def remove_modlog_entry(self, case_id, guild_id):
        self.cur.execute(
            'DELETE FROM Modlog_Entry WHERE case_id=%s, guild_id=%s', (case_id, guild_id))
        self.logger.log(level=logging.INFO,
                        msg=f'Removed entry {guild_id}:{case_id} from database')

    # Get Functions
    def get_guild(self, guild_id):
        self.cur.execute(
            'SELECT * FROM Guild WHERE guild_id=%s', [str(guild_id)])
        return self.cur.fetchone()

    def get_member(self, member_id):
        self.cur.execute(
            'SELECT * FROM Member WHERE discord_id=%s', [str(member_id)])
        return dict(self.cur.fetchone())

    def get_role(self, role_id):
        self.cur.execute(
            'SELECT * FROM Discord_Role WHERE role_id=%s', [str(role_id)])
        return dict(self.cur.fetchone())

    def get_entry_by_guild_case(self, case_id, guild_id):
        return self.cur.execute('SELECT * FROM Modlog_Entry WHERE case_id=%s AND guild_id=%s', (case_id, guild_id))

    def get_rr_roleid(self, guild_id, message_id, reaction):
        for r in self.cur.execute('SELECT role_id FROM Reaction_Role WHERE guild_id=%s AND message_id=%s AND reaction=%s', (guild_id, message_id, reaction)):
            return r['role_id']

    def get_rr(self, guild_id, message_id, reaction):
        return [record for record in self.cur.execute('SELECT * FROM Reaction_Role WHERE guild_id=%s AND message_id=%s AND reaction=%s', (guild_id, message_id, reaction))]

    # Get All Functions

    def get_all_guilds(self):
        return [record for record in self.cur.execute('SELECT * FROM Guild')]

    def get_all_members(self):
        return [record for record in self.cur.execute('SELECT * FROM Member')]

    def get_all_roles(self):
        return [record for record in self.cur.execute('SELECT * FROM Discord_Role')]

    def get_guild_rr_msgs(self, guild_id):
        return [record['message_id'] for record in self.cur.execute('SELECT message_id FROM Reaction_Role WHERE guild_id=%s', (guild_id,))]

    def get_rrs_by_msg(self, msg_id):
        return [dict(record) for record in self.cur.execute('SELECT * FROM Reaction_Role WHERE message_id=%s', (msg_id,))]

    # Helper Functions
    def add_guild_member(self, guild_id, member_id):
        self.cur.execute(
            'INSERT OR IGNORE INTO Guild_Member (guild_id, member_id) VALUES (%s, %s) ON CONFLICT DO NOTHING', (guild_id, member_id))
        self.conn.commit()

    def add_member_role(self, member_id, role_id):
        self.cur.execute(
            'INSERT OR IGNORE INTO Member_Role (role_id, member_id) VALUES (%s, %s) ON CONFLICT DO NOTHING', (role_id, member_id))
        self.conn.commit()

    def remove_guild_member(self, guild_id, member_id):
        self.cur.execute(
            'DELETE FROM Guild_Member WHERE guild_id=%s AND member_id=%s)', (guild_id, member_id))
        self.conn.commit()

    def remove_member_role(self, member_id, role_id):
        self.cur.execute(
            'DELETE FROM Member_Role WHERE role_id=%s AND member_id=%s', (role_id, member_id))
        self.conn.commit()


db = db(logging.getLogger('test'))
db.add_guild(123)
db.cur.execute("SELECT * FROM Guild;")
print(db.cur.fetchone())
