import re
from datetime import datetime

import discord
from discord.ext import commands


class HelpChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Listeners
    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if type(message.channel) != discord.TextChannel:
    #         return
    #     help_channels = self.bot.db.get_all_help_channels(message.guild.id)
    #     if message.channel.id in help_channels:
    #         return

    # Commands
    @commands.command()
    async def createhc(self, ctx, assign: str, resolve: str, category: str):
        if category:
            category = await ctx.guild.create_category(name='Available Help Channels')
        channel = await ctx.guild.create_text_channel(name='help-1', category=category)

        self.bot.db.add_help_channel(ctx.guild.id, )
        await ctx.send(f'Added {channel.mention} to help channels')
    
    @commands.command()
    async def sethc(self, ctx, channel: discord.TextChannel, assign: str, resolve: str):
        help_channel = {
            'channel': channel.id, 
            'assign': assign if assign.lower() in ['move', 'hide'] else 'move',
            'resolve': resolve if resolve.lower() in ['return', 'delete'] else 'return'
            }
        self.bot.db.add_help_channel(ctx.guild.id, help_channel)
    
    @commands.command()
    async def setassign(self, ctx, channel: discord.TextChannel, assign: str):
        return

    @commands.command()
    async def setresolve(self, ctx, channel: discord.TextChannel, resolve: str):
        return

    @commands.command()
    async def resolve(self, ctx):
        return
