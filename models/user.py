class User:
    def __init__(self, bot, user=None, query=True, **kwargs):
        dbu = True
        if user:
            if query:
                dbu = bot.db.get_user(user.id)
                if dbu:
                    self.__dict__ = dbu.__dict__
            if not query or (query and not dbu):
                self._id = user.id
                self.version = 'NRSV'
        else:
            self.__dict__ = kwargs
    
    def __repr__(self):
        return '<User' + f'({", ".join([f"{k}={self.__dict__[k]}" for k in self.__dict__])})' + '>'