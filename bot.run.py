import discord
from discord.ext import commands

import os

bot = commands.Bot(command_prefix='.')

bot.remove_command("help")

for cog in os.listdir('.\\cogs'):
    if cog.endswith(".py") and not cog.startswith("__"):
        try:
            cog = f"cogs.{cog.replace('.py','')}"
            bot.load_extension(cog)
        except Exception as e:
            print(f"{cog} cannot be loaded")
            raise e

bot.run('token')
