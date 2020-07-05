import discord
from discord.ext import commands


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
        if level > int(member['xp']**(1/2) / 5) and guild['level_msg']:
            await message.channel.send(f'{message.author.mention} just reached level **{level}**!')
        
        self.bot.db.update_member(message.author, xp=member['xp']+guild['msg_xp'])

        ranks = guild['ranks']
        if not ranks:
            return
        
        roles = [message.guild.get_role(int(r)) for r in ranks if ranks[r]==level]
        roles = [r for r in roles if r not in message.author.roles]
        await message.author.add_roles(*roles)
        await message.author.remove_roles()
        
    @commands.command()
    async def level(self, ctx, member=None):
        pass

    @commands.command()
    async def levels(self, ctx, arg, xp:int=5):
        if arg.lower() == 'off':
            self.bot.db.update_guild(ctx.guild.id, msg_xp=None)
            await ctx.send('Turned chat leveling off.')
        elif arg.lower() == 'on':
            self.bot.db.update_guild(ctx.guild.id, msg_xp=xp)
            await ctx.send(f'Turned chat leveling on with **{xp}**xp every message.')
        elif arg.lower() == 'reset':
            await ctx.send("This will **permanently** reset all members' xp. To confirm type **y**. To cancel type **n**")
            try:
                msg = await self.bot.wait_for(
                    'message', 
                    timeout=60, check=lambda m: m.author == ctx.author 
                    and m.content.lower() in ['y', 'n', 'yes', 'no']
                )
            except:
                await ctx.send('Timeout: Please re-issue your command.')
            if msg.content.lower() not in ['y', 'yes']:
                return
            for member in ctx.guild.members:
                self.bot.db.update_member(member, xp=0)
            await ctx.send(f'Turned chat leveling on with **{xp}**xp every message.')
    
    @commands.command()
    async def levelmsg(self, ctx, arg):
        if arg.lower() == 'off':
            self.bot.db.update_guild(ctx.guild.id, level_msg=False)
            await ctx.send('Turned chat level messages off.')
        elif arg.lower() == 'on':
            self.bot.db.update_guild(ctx.guild.id, level_msg=True)
            await ctx.send('Turned chat level messages on.')

    @commands.command()
    async def rank(self, ctx, arg, role: discord.Role, level: int=None):
        if arg.lower() == 'add':
            self.bot.db.add_rank(ctx.guild.id, role, level)
            await ctx.send(f'Users will now get the **{role}** role when they reach level **{level}**.')
        elif arg.lower() == 'remove':
            self.bot.db.delete_rank(ctx.guild.id, role.id)
            await ctx.send(f'Removed rank for **{role}** role.')
    
    @commands.command()
    async def ranks(self, ctx):
        ranks = self.bot.db.get_guild(ctx.guild.id)['ranks']

        if not ranks:
            await ctx.send('This server has no ranks.')
            return

        roles = [ctx.guild.get_role(int(k)).mention for k in ranks.keys()]
        levels = [str(ranks[k]) for k in ranks]

        embed = discord.Embed(title='Ranks')
        embed.add_field(name='Role', value='\n\n'.join(roles), inline=True)
        embed.add_field(name='Role', value='\n\n'.join(levels), inline=True)
        await ctx.send(embed=embed)
    