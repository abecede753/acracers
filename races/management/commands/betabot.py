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


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='beta',
                   description="Beta Bot",
                   intents=intents, help_command=None)


@bot.command()
@commands.check(is_writeable_channel)
async def list(ctx):
    MAX_LEN = 38
    embed = discord.Embed()
    embed.title = "These are all combos for now."
    description = ("`  ID` `{0:" + str(MAX_LEN) + "}` `Rating`\n").format('Title')
    rslist = []
    for rs in RaceSetup.objects.annotate(
        numhates=Count(Case(When(
            vote__value=-3, then=1), output_field=IntegerField())),
        numdislikes=Count(Case(When(
            vote__value=-1, then=1), output_field=IntegerField())),
        numlikes=Count(Case(When(
            vote__value=1, then=1), output_field=IntegerField())),
        numloves=Count(Case(When(
            vote__value=3, then=1), output_field=IntegerField())),
    ).order_by('title'):
        if len(rs.title) > MAX_LEN:
            title = rs.title[:MAX_LEN - 1] + '…'
        else:
            title = rs.title
        details = utils.DetailVotes(rs.numhates, rs.numdislikes,
                                    rs.numlikes, rs.numloves)
        smiley, score = details.smiley
        rslist.append(('`{id:4d}` `{title:' + str(MAX_LEN) +
                       '}` `{score:+1.1f}`{smiley}').format(
            id=rs.id, title=title, smiley=smiley, score=score))
    description += '\n'.join(rslist)
    embed.description = description
    embed.set_footer(text='Add a combo to the queue with '
                     '`append ID` or `insert ID`.\n'
                     'For more information about a combo use `info ID`.')
    await ctx.send(embed=embed)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        bot.run(settings.DISCORDTOKEN)
        print("Done.")
