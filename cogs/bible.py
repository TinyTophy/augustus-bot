import re

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands


class Bible(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if type(message.channel) != discord.DMChannel and not message.author.bot:
            regex = re.compile(r"\[(?P<book>(?:\d\s*)?[A-Z]?[a-z]+)\s*(?P<chapter>\d)+(?:[:-]?(?P<verses>\d+?(?:\s*-\s*\d+)?)?(?::\d+|(?:\s*[A-Z]?[a-z]+\s*\d+:\d+))?)?\s?(?P<version>[A-Z]?[a-z]+)?\]")
            match = regex.match(message.content)
            print(match)

            if not match:
                return

            async with message.channel.typing():
                groups = match.groupdict()
                if not groups['version']:
                    groups['version'] = self.bot.db.get_user(message.author.id)['version']
                print(groups)

                url = 'https://www.biblegateway.com/passage/?search={book}%{chapter}:{verses}&version={version}'.format(**groups)

                # response = requests.get(url)

    @commands.command()
    async def setversion(self, ctx, version: str):
        return

        # https://www.biblegateway.com/passage/?search=1%20Kings%201&version=NRSV
        # https://www.biblegateway.com/passage/?search=Leviticus+1&version=NRSV
        # https://www.biblegateway.com/passage/?search=John%201:1&version=NIV
        # https://www.biblegateway.com/passage/?search=John+1&version=NIV
