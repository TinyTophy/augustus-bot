import json
import logging

from discord.ext import commands
import discord

from cogs.help import Help
from cogs.misc import Misc
from cogs.mod import Mod
from cogs.modlog import ModLog
from cogs.quickpoll import Quickpoll
from cogs.quotes import Quotes
from cogs.reactionrole import ReactionRole
from cogs.vote import Vote
from cogs.latex import Latex
# from cogs.log import Log
from mode import token_mode
from mongodb import db
from utils import get_prefix, load_guilds


logger = logging.getLogger('discord')
logging.basicConfig(level=logging.INFO)
db = db(logger)
info = json.load(open('info.json'))
token = info['token'][token_mode()]
address = info['address']
bot = commands.Bot(command_prefix=get_prefix, help_command=Help())

@bot.event
async def on_ready():
    load_guilds(db, bot.guilds)
    await bot.change_presence(activity=discord.Game(name=f'Minecraft: {address}'))
    print(f'Logged in as {bot.user}')
    print('-----------------------')

if __name__ == "__main__":
    bot.add_cog(Misc(bot, db))
    bot.add_cog(Mod(bot, db))
    bot.add_cog(ReactionRole(bot, db))
    bot.add_cog(Vote(bot, db))
    bot.add_cog(ModLog(bot, db))
    bot.add_cog(Quickpoll(bot))
    bot.add_cog(Quotes(bot, db))
    bot.add_cog(Latex(bot))
    # bot.add_cog(Log(bot, db))
    bot.run(token)
