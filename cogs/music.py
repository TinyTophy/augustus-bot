from discord.ext import commands
import discord
import youtube_dl


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, link):
        channel = ctx.author.voice.channel
        if not channel:
            await ctx.send("You aren't connected to a voice channel. Connect to a voice channel to play media.")
            return
        
        vc_client = await channel.connect(timeout=60, reconnect=False)
        # vc_client.play(discord.FFmpegAudio(link))