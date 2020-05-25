from sympy import preview
from discord.ext import commands
import discord


class Latex(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def latex(self, ctx, *, tex):
        preamble = r'\documentclass{article}\usepackage{xcolor}\begin{document}\color{white}'
        preview(tex, viewer='file', filename='tex.png', euler=False, preamble=preamble, dvioptions=["-T", "tight", "-D 500", "-bg", "Transparent"])
        async with ctx.channel.typing():
            await ctx.send(file=discord.File(open('tex.png', 'rb')))