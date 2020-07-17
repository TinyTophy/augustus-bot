import discord


class Member:
    def __init__(self, bot, member: discord.Member = None, **kwargs):
        if member:
            dbm = bot.db.get_member(member)
            if dbm:
                self.__dict__ = dbm
            else:
                self.id = member.id
                self.roles = [r.id for r in member.roles]
                self.quotes = []
                self.warns = 0
                self.xp = 0
        else:
            self.__dict__ = kwargs   