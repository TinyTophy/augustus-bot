import asyncio
import json
import math
import re
from datetime import datetime

import aiohttp
import discord
import humanize
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# Commands

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')

    @commands.command()
    async def say(self, ctx, *msg):
        await ctx.send(' '.join(msg))

    @commands.command()
    async def info(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        create_delta = relativedelta(datetime.now(), member.created_at)
        join_delta = relativedelta(datetime.now(), member.joined_at)

        def pretty_delta(delta):
            pdelta = {}
            if delta.years > 0:
                pdelta['years'] = delta.years
            if delta.months > 0:
                pdelta['months'] = delta.months
            if delta.days > 0:
                pdelta['days'] = delta.days
            if delta.hours > 0:
                pdelta['hours'] = delta.hours
            if delta.minutes > 0:
                pdelta['minutes'] = delta.minutes

            pstr = ''
            for i, k in enumerate(pdelta):
                if i == len(pdelta) - 1:
                    pstr = pstr[:-1]
                    pstr += f' and {pdelta[k]} {k} ago'
                else:
                    pstr += f' {pdelta[k]} {k},'
            return pstr[1:]

        cdelta = pretty_delta(create_delta)
        jdelta = pretty_delta(join_delta)
        cutc = member.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
        jutc = member.joined_at.strftime('%Y-%m-%d %H:%M:%S UTC')
        ctx.guild.members.sort(key=lambda m: m.created_at)
        rank = ctx.guild.members.index(member) + 1
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])
        if rank == 1:
            rankstr = 'Oldest account on the server'
        else:
            rankstr = f'{ordinal(rank)} oldest account on the server'

        embed = discord.Embed(color=member.color)
        embed.set_author(name=f'{member}', url=member.avatar_url_as(
            format='png'), icon_url=member.avatar_url)
        embed.set_footer(text=f'ID: {member.id}')
        embed.add_field(name='Nickname', value=member.nick, inline=True)
        embed.add_field(name='Created At',
                        value=f'{cutc}\n({cdelta})\n{rankstr}', inline=True)
        embed.add_field(name='Joined At',
                        value=f'{jutc}\n({jdelta})', inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def serverinfo(self, ctx):
        if ctx.author.guild_permissions.administrator:
            vcmembers = {c.name: c.members for c in ctx.guild.voice_channels}
            bychannel = '\n'.join(
                [f'{k}: {len(vcmembers[k])}' for k in vcmembers])
            total = sum([len(vcmembers[k]) for k in vcmembers])
            roles = '\n'.join([role.mention for role in ctx.guild.roles])

            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_author(name=ctx.guild.name,
                             url=ctx.guild.icon_url, icon_url=ctx.guild.icon_url)
            embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
            embed.add_field(name="Roles", value=roles, inline=True)
            embed.add_field(name="Created At", value=ctx.guild.created_at.strftime(
                '%Y-%m-%d %H:%M:%S UTC'), inline=True)
            embed.add_field(name="Members in Voice Channels",
                            value=f'__**Total:**__ {total}\n__**By Channel**__\n{bychannel}', inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send('Insufficient permissions for this command')

    @commands.is_owner()
    @commands.command()
    async def rolecolor(self, ctx, role: discord.Role):
        await ctx.send(role.color)

    @commands.command()
    async def covid(self, ctx, country=''):
        if country == '':
            url = 'https://www.worldometers.info/coronavirus/'
            img_url = 'https://www.rivertowns.net/incoming/4991938-wtw6q9-RTSA-coronavirus-CDC.jpg/alternates/BASE_LANDSCAPE/RTSA%20coronavirus%20CDC.jpg'
            name = 'World Stats'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    response = await r.text()
            soup = BeautifulSoup(response, 'html.parser')
            last = soup.body.find(text=re.compile('Last updated')).replace(
                'Last updated:', '').strip()
            lastdate = datetime.strptime(last, '%B %d, %Y, %H:%M GMT')
            results = soup.body.find_all(id='maincounter-wrap')
            items = [r.span.contents[0].strip() for r in results if r.span]
        else:
            url = f'https://www.worldometers.info/coronavirus/country/{country.lower()}/'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    response = await r.text()
            soup = BeautifulSoup(response, 'html.parser')
            last = soup.body.find(text=re.compile('Last updated')).replace(
                'Last updated:', '').strip()
            lastdate = datetime.strptime(last, '%B %d, %Y, %H:%M GMT')
            results = soup.body.find_all(id='maincounter-wrap')
            items = [r.span.contents[0].strip() for r in results if r.span]
            img = soup.body.find(src=re.compile('/img/flags/small/'))
            name = img.parent.next_sibling.strip()
            img = str(img)[str(img).index('src'):str(
                img).index('.gif')].strip('src="')
            img_url = f'https://www.worldometers.info{img}.gif'

        embed = discord.Embed(title=name, timestamp=lastdate, color=0xe91e63)
        embed.set_thumbnail(url=img_url)
        embed.add_field(name='Cases', value=items[0])
        embed.add_field(name='Deaths', value=items[1])
        embed.add_field(name='Recovered', value=items[2])
        embed.add_field(name='Source', value=f'[Worldometers]({url})')
        embed.set_footer(text='Last Updated')
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['qp'])
    async def quickpoll(self, ctx, *msg):
        embed = discord.Embed(title='Quick Poll', description=' '.join(msg), colour=discord.Colour(0x2ecc71))
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        message = await ctx.send(embed=embed)
        await message.add_reaction('👍')
        await message.add_reaction('👎')
        await message.add_reaction('🤷')
        await ctx.message.delete()


    @commands.is_owner()
    @commands.command()
    async def leave(self, ctx, guild_id):
        guild = discord.utils.get(self.bot.guilds, id=guild_id)
        await guild.leave()
