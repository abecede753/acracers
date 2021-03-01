import discord
from discord.ext import commands
from django.conf import settings
from django.core.management.base import BaseCommand

# from races.management.commands import botfunctions
from races.management.commands.decorators import (
    is_writeable_channel,)


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='beta',
                   description="Beta Bot",
                   intents=intents, help_command=None)


@bot.command()
@commands.check(is_writeable_channel)
async def beta(ctx):
    embed = discord.Embed(color=0x00ff00)
    embed.title = "This is beta."
    await ctx.send(embed=embed)
    return


@bot.command()
@commands.check(is_writeable_channel)
async def tags(ctx):
    embed = discord.Embed(color=0x00ff00)
    embed.title = "This is beta."
    await ctx.send(embed=embed)
    return


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        bot.run(settings.DISCORDTOKEN)
        print("Done.")
