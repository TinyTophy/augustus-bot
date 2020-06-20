import discord
from discord.ext import commands
from utils import is_staff


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if type(message.channel) == discord.DMChannel or message.author.bot:
            return

        guild = self.bot.db.get_guild(message.guild.id)
        if not guild['msg_xp']:
            return

        member = self.bot.db.get_member(message.author)
        level = int((member['xp'] + guild['msg_xp'])**(1/2) / 5)
        if level > int(member['xp']**(1/2) / 5):
            await message.channel.send(f'{message.author.mention} just reached level **{level}**!')
        
        self.bot.db.update_member(message.author, xp=member['xp']+guild['msg_xp'])

        ranks = guild['ranks']
        if not ranks:
            return
        
        roles = [message.guild.get_role(int(r)) for r in ranks if ranks[r]==level]
        roles = [r for r in roles if r not in message.author.roles]
        await message.author.add_roles(*roles)
        
    @commands.command()
    async def level(self, ctx, member=None):
        pass
    
    @is_staff()
    @commands.command()
    async def levels(self, ctx, arg, xp:int=5):
        if arg.lower() == 'off':
            self.bot.db.update_guild(ctx.guild.id, msg_xp=0)
            await ctx.send('Turned chat leveling off.')
        elif arg.lower() == 'on':
            self.bot.db.update_guild(ctx.guild.id, msg_xp=xp)
            await ctx.send(f'Turned chat leveling on with **{xp}**xp every message.')
    
    @is_staff()
    @commands.command()
    async def levelmsg(self, ctx, arg):
        if arg.lower() == 'off':
            self.bot.db.update_guild(ctx.guild.id, level_msg=False)
            await ctx.send('Turned chat level messages off.')
        elif arg.lower() == 'on':
            self.bot.db.update_guild(ctx.guild.id, level_msg=True)
            await ctx.send('Turned chat level messages on.')

    @is_staff()
    @commands.command()
    async def rank(self, ctx, arg, role: discord.Role, level: int=None):
        if arg.lower() == 'add':
            self.bot.db.add_rank(ctx.guild.id, role, level)
            await ctx.send(f'Users will now get the **{role}** role when they reach level **{level}**.')
        elif arg.lower() == 'remove':
            self.bot.db.delete_rank(ctx.guild.id, role.id)
            await ctx.send(f'Removed rank for **{role}** role.')