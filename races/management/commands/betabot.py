import statistics
import discord
from discord.ext import commands
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count, Case, When, IntegerField


# from races.management.commands import botfunctions
from races.models import RaceSetup
from races.management.commands.decorators import (
    is_writeable_channel,)
from races.management.commands import utils
from races.management.commands.botfunctions import error, _votedetails


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='beta',
                   description="Beta Bot",
                   intents=intents, help_command=None)


@bot.command()
@commands.check(is_writeable_channel)
async def info(ctx, id: int):
    """Shows more info about a combo"""
    await ctx.send(embed=_infoembed(id))


def _infoembed(id):
    try:
        rs = RaceSetup.objects.get(pk=id)
    except Exception:
        embed = error(
            "Sorry, I could not find a combo with that ID.")
        return embed
    embed = discord.Embed()
    embed.title = rs.title
    embed.set_image(url='https://acracers.com' + rs.image.url)

    votedetails = _votedetails(id)
    dv = utils.DetailVotes(*votedetails)

    embed.add_field(name='Detailed votes',
                    value=dv.barsplus,
                    inline=True)
    try:
        mediantxt = '{0:6.2f}'.format(statistics.median(dv.datadump))
    except Exception:
        mediantxt = ' n/a'
    try:
        stddevtxt = '{0:6.2f}'.format(statistics.stdev(dv.datadump))
    except Exception:
        stddevtxt = ' n/a'

    stattext = ('`Mean  : {0:6.2f}`\n`Median: {1}`\n'
                '`StdDev: {2}`\n`Votes :{3:4d}   `').format(
                    dv.smiley[1], mediantxt, stddevtxt, len(dv.datadump))

    embed.add_field(name='Statistics', value=stattext, inline=True)

    desc = rs.description
    if rs.car_download_url:
        desc += '\n\nCar download: {0}'.format(rs.car_download_url)
    if rs.track_download_url:
        desc += '\n\nTrack download: {0}'.format(rs.track_download_url)
    embed.description = desc
    return embed


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        bot.run(settings.DISCORDTOKEN)
        print("Done.")
