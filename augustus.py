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
from cogs.modmail import Modmail
from cogs.quickpoll import Quickpoll
from cogs.quotes import Quotes
from cogs.reactionrole import ReactionRole
from cogs.levels import Levels
from cogs.vote import Vote
from cogs.music import Music
from mode import token_mode
from mongodb import db
from utils import get_prefix, load_guilds


class Augustus(commands.Bot):
    def __init__(self):
        self.logger = logging.getLogger('discord')
        logging.basicConfig(level=logging.INFO)
        self.db = db(self.logger)
        info = json.load(open('info.json'))
        token = info['token'][token_mode()]
        super().__init__(command_prefix=get_prefix, help_command=Help())
        self.add_cog(Modmail(self))
        self.add_cog(ModLog(self))
        self.add_cog(Mod(self))
        self.add_cog(Misc(self))
        self.add_cog(Quickpoll(self))
        self.add_cog(Quotes(self))
        self.add_cog(Embed(self))
        self.add_cog(ReactionRole(self))
        self.add_cog(Levels(self))
        self.add_cog(Music(self))
        self.run(token)

    async def on_ready(self):
        load_guilds(self.db, self.guilds)
        await self.change_presence(activity=discord.Game(name=f'DM me for staff'))
        print(f'Logged in as {self.user}')
        print('-----------------------')
    