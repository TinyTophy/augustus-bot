import discord
from models.member import Member
from models.role import Role


class Guild:
    def __init__(self, bot, guild: discord.Guild = None, **kwargs):
        if guild:
            dbg = bot.db.get_guild(guild.id) 
            if dbg:
                self.__dict__ = dbg.__dict__
            else:
                self._id = guild.id
                self.prefixes = [f':{bot.db.mode}: ', '$']
                self.muterole_id = None
                self.log_channels = []
                self.msg_xp = None
                self.level_msg = False
                self.members = [Member(bot, m).__dict__ for m in guild.members]
                self.help_channels = []
                self.roles = [Role(bot, r) for r in guild.roles]
                self.ranks = []
                self.automod_rules = []
        else:
            self.__dict__ = kwargs