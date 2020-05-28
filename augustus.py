import json
import logging

import discord
from discord.ext import commands

from cogs.help import Help
# from cogs.latex import Latex
# from cogs.log import Log
# from cogs.misc import Misc
from cogs.mod import Mod
# from cogs.modlog import ModLog
from cogs.quickpoll import Quickpoll
# from cogs.quotes import Quotes
# from cogs.reactionrole import ReactionRole
# from cogs.vote import Vote
from mode import token_mode
from postgesql import db
from utils import get_prefix


class Augustus(commands.Bot):
    def __init__(self):
        self.logger = logging.getLogger('discord')
        logging.basicConfig(level=logging.INFO)
        self.db = db(self.logger)
        info = json.load(open('info.json'))
        token = info['token'][token_mode()]
        super().__init__(command_prefix=get_prefix, help_command=Help())
        # self.add_cog(Mod(self))
        self.add_cog(Quickpoll(self))
        self.run(token)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name='!help'))
        for g in self.guilds:
            self.db.add_guild(g)
            for m in g.members:
                self.db.add_user(m)
        print(f'Logged in as {self.user}')
        print('-----------------------')
