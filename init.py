from augustus import Augustus
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
from mode import token_mode
from mongodb import MongoDB

if __name__ == "__main__":
    Augustus(
        token=token_mode(),
        db=MongoDB,
        help=Help,
        cogs=[
        # Automod,
        Bible,
        Embed,
        HelpChannel,
        # Latex,
        Levels,
        # Log,
        Misc,
        # Mod,
        # Music,
        Quotes,
        # ReactionRole
        ]
    )
