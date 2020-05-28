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
from utils import get_prefix, load_guilds


class Augustus(commands.Bot):
    def __init__(self):
        self.logger = logging.getLogger('discord')
        logging.basicConfig(level=logging.INFO)
        self.db = db(self.logger)
        info = json.load(open('info.json'))
        token = info['token'][token_mode()]
        super().__init__(command_prefix=['!', '.'], help_command=Help())
        # self.add_cog(Mod(self))
        self.add_cog(Quickpoll(self))
        self.run(token)

    async def on_ready(self):
        # load_guilds(db, self.guilds)
        await self.change_presence(activity=discord.Game(name=f'{self.command_prefix[0]}help'))
        # for g in self.guilds:
        #     await g.leave()
        print(f'Logged in as {self.user}')
        print('-----------------------')
