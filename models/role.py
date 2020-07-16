import discord


class Role:
    def __init__(self, bot, role: discord.Role = None, **kwargs):
        if role:
            dbr = bot.db.get_role(role.id) 
            if dbr:
                self.__dict__ = dbr.__dict__
            else:
                self._id = role.id
                self.sticky = False
                self.auto = False
                self.reaction_roles = []
        else:
            self.__dict__ = kwargs