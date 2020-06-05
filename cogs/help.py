import discord
from discord.ext import commands


# class Help(commands.DefaultHelpCommand):
#     async def send_bot_help(self, mapping):
#         bot = self.context.bot
#         filtered = await self.filter_commands(bot.commands, sort=True)
#         cmds = []

#         for command in filtered:
#             cmds.append(f'{self.clean_prefix}{command.name}')

#         embed = discord.Embed(title='Help', description='\n'.join(cmds))

#         await self.get_destination().send(embed=embed)

#     async def send_cog_help(self, cog):
#         filtered = await self.filter_commands(cog.get_commands(), sort=True)
#         cmds = []

#         for command in filtered:
#             cmds.append(f'{self.clean_prefix}{command.name}')

#         embed = discord.Embed(title=cog.qualified_name, description='\n'.join(cmds))

#         await self.get_destination().send(embed=embed)
    

class Help(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return '{0.clean_prefix}{1.qualified_name} {1.signature}'.format(self, command)
