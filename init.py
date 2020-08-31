from bot import Bot
from cogs.automod import Automod
from cogs.bible import Bible
from cogs.embed import Embed
from cogs.help import Help
from cogs.helpchannel import HelpChannel
from cogs.latex import Latex
from cogs.levels import Levels
from cogs.log import Log
from cogs.misc import Misc
from cogs.mod import Mod
from cogs.helpchannel import HelpChannel
from cogs.music import Music
from cogs.quotes import Quotes
from cogs.reactionrole import ReactionRole
from mode import token_mode, db_mode
from database.postgresql import Postgresql

if __name__ == "__main__":
    bot = Bot(
        db=Postgresql(db_mode()),
        help=Help,
        cogs=[
        # Automod,
        Bible,
        # Embed,
        # HelpChannel,
        # Latex,
        # Levels,
        # Log,
        Misc,
        # Mod,
        # Music,
        # Quotes,
        # ReactionRole
        ]
    )
    bot.run(token_mode())

