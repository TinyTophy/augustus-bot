from discord.ext import commands
import discord
import json


def allowed():
    def predicate(ctx):
        modrole = ctx.guild.get_role(ctx.cog.bot.db.get_guild(ctx.guild.id)['modrole_id'])
        return modrole in ctx.author.roles or ctx.author.guild_permissions.administrator
    return commands.check(predicate)






