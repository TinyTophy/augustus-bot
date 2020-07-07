import re
import string

import bs4
import discord
from bs4 import BeautifulSoup
from discord.ext import commands
import aiohttp


class Bible(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if type(message.channel) == discord.DMChannel or message.author.bot:
            return

        pattern1 = re.compile(r"^\[(?P<book>(?:\d\s*)?[A-Z]?[a-z]+)\s*(?P<chapter>\d+):(?P<verses>(?P<start>\d+)(?:-(?P<end>\d+))?)(?:\s(?P<version>[A-Z]?[a-z]+))?\]$")
        match = pattern1.match(message.content)

        if not match:
            return

        async with message.channel.typing():
            groups = match.groupdict()
            if not groups['version']:
                groups['version'] = self.bot.db.find_user(message.author.id)['version']
            
            groups['book'] = groups['book'].replace(' ', '%')
            url = "https://www.biblegateway.com/passage/?search={book}+{chapter}:{verses}&version={version}".format(**groups)

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    response = await r.text()
            soup = BeautifulSoup(response, 'html.parser')

            text_div = re.compile(r"\bresult-text-style-(?:normal|rtl)\b")
            results = soup.find('div', {'class': text_div})

            if not results:
                await message.channel.send("Hmm couldn't find that passage. Make sure it exists and the command format is right.")
                return

            verselist = results.findAll(text=True)

            trash = ['\n', '[', ']', ' ', '(', ')'] + list(string.ascii_uppercase) + list(string.ascii_lowercase)
            verselist = list(filter(lambda x: x not in trash, verselist))

            def check_int(str): 
                try:    
                    int(str)
                    return True
                except:
                    return False
            
            span = [i for i, item in enumerate(verselist) if check_int(item)]
            end = verselist.index('Read full chapter')
            
            if groups['end']:
                versenums = list(range(int(groups['start']),int(groups['end'])+1))
            else:
                versenums = [int(groups['start'])]

            for i, item in enumerate(span):
                verselist[item] = f'**{versenums[i]}.**'

            verselist = verselist[span[0]:end]

            desc = ' '.join(verselist)

            footer_text = re.compile(r"(?:\d+\s)?(?:[A-Z]+[a-z]+\s)(?:\d+):(?:\d+(?:-\d+)?)")
            dd_display = [c for d in soup.find_all('div', {'class': 'dropdown-display-text'}) for c in d.contents]
            version = groups['version'].upper()
            footer = list(filter(footer_text.match, dd_display))[0] + f' ({version})'
            
            embed = discord.Embed(description=desc)
            embed.set_footer(text=footer)
            await message.channel.send(embed=embed)
                

    @commands.command()
    async def setversion(self, ctx, version: str):
        self.bot.db.update_user(ctx.author.id, version=version)
        await ctx.send(f'Set default version to **{version}**.')
