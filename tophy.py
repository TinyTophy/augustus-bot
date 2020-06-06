import json
import logging

import discord
from discord.ext import commands

from cogs.embed import Embed
from cogs.help import Help
from cogs.latex import Latex
from cogs.log import Log
from cogs.misc import Misc
from cogs.mod import Mod
from cogs.modlog import ModLog
from cogs.quickpoll import Quickpoll
from cogs.quotes import Quotes
from cogs.reactionrole import ReactionRole
from cogs.vote import Vote
from mode import token_mode
from mongodb import db
from utils import get_prefix, load_guilds


class Tophy(commands.Bot):
    def __init__(self):
        self.logger = logging.getLogger('discord')
        logging.basicConfig(level=logging.INFO)
        self.db = db(self.logger)
        info = json.load(open('info.json'))
        token = info['token'][token_mode()]
        super().__init__(command_prefix=get_prefix, help_command=Help())
        # self.add_cog(Mod(self))
        # self.add_cog(Misc(self))
        # self.add_cog(Quickpoll(self))
        self.add_cog(Embed(self))
        self.add_cog(ReactionRole(self))
        self.run(token)

    async def on_ready(self):
        load_guilds(self.db, self.guilds)
        print(f'Logged in as {self.user}')
        print('-----------------------')
    
    async def on_command_error(self, ctx, exception):
        print(exception)
        
        