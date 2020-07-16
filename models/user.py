class User:
    def __init__(self, bot, user=None, **kwargs):
        if user:
            dbu = bot.db.get_user(user.id)
            if dbu:
                self.__dict__ = dbu
            else:
                self._id = user.id
                self.version = 'NRSV'
        else:
            self.__dict__ = kwargs
    
    def __repr__(self):
        return '<User' + f'({", ".join([f"{k}={self.__dict__[k]}" for k in self.__dict__])})' + '>'