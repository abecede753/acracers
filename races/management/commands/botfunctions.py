import datetime
import statistics
import subprocess
import sys
import traceback

import discord
from discord.ext import commands
from django.db.models import Count, Case, When, IntegerField
from django.utils import timezone
import requests

from races.models import RaceSetup, RaceQueue, Vote
from races.management.commands.decorators import (
    is_writeable_channel, is_elevated_role)
from races.management.commands import utils
from races.management.commands.live_options import parse_options
from races.management.commands.barchart import bars

description = ('Here are the commands to set up "rounds" of car/track combos '
               'for hosting a couple of races with friends.\nEach round '
               'consists of 10min qualifying, 10min race one, 10min race two '
               'with inverted starting grid.')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='', description=description,
                   intents=intents, help_command=None)


@bot.command()
@commands.check(is_writeable_channel)
async def append_extra(ctx, *, cmdline: str):
    """Append a special round"""
    try:
        rs_id = cmdline.split(' ')[0]
    except Exception:
        await ctx.send(embed=error(
            "couldnt find an id."))
        return
    try:
        params = cmdline.split(' ')[1:]
    except Exception:
        await ctx.send(embed=error(
            "There's nothing special I could see. ({0})".format(cmdline)))
        return
    if len(params) < 1:
        await ctx.send(embed=error(
            "There's nothing special I could see. :("))
        return
    try:
        opts = parse_options(params)
    except Exception:
        await ctx.send(embed=error(
            "Sorry."))
        return
    try:
        rs = RaceSetup.objects.get(pk=rs_id)
    except Exception:
        await ctx.send(embed=error(
            "Sorry, I could not find a combo with that ID."))
        return
    max_index = 0
    try:
        max_index = RaceQueue.objects.all().order_by('-index')[0].index
    except Exception:
        pass
    rq = RaceQueue(setup=rs, index=max_index + 1, options=' '.join(params))
    rq.save()
    reply = 'I added the combo **{0}** to the queue.'.format(rq.setup)
    additional = []
    if opts.p:
        additional.append("practice: {0} minutes".format(opts.p))
    if opts.r:
        additional.append("race: {0} minutes".format(opts.r))
    if opts.o:
        additional.append("car setup: open")
    reply += '\n' + ', '.join(additional)
    await ctx.send(reply)


@bot.command()
@commands.check(is_writeable_channel)
async def list(ctx):
    """Shows all car/track combos with their score

    You can then add a combo (using its ID) to the queue for
    having fun with your friends.
    """
    MAX_LEN = 38
    MAX_LINES_PER_EMBED = 32
    embed = discord.Embed()
    embed.title = "These are all combos for now."
    description = ("`  ID` `{0:" + str(MAX_LEN) + "}` `HDLL`\n").format(
        'Title')
    rslist = []
    we_have_new_tracks = False
    racesetups = RaceSetup.objects.exclude(hidden=True).annotate(
        numhates=Count(Case(When(
            vote__value=-3, then=1), output_field=IntegerField())),
        numdislikes=Count(Case(When(
            vote__value=-1, then=1), output_field=IntegerField())),
        numlikes=Count(Case(When(
            vote__value=1, then=1), output_field=IntegerField())),
        numloves=Count(Case(When(
            vote__value=3, then=1), output_field=IntegerField())),
        numvotes=Count('vote'),
    ).order_by('title')
    max_votes_for_racesetup = max(
        racesetups.latest("numhates").numhates,
        racesetups.latest("numdislikes").numdislikes,
        racesetups.latest("numlikes").numlikes,
        racesetups.latest("numloves").numloves,
    )
    for rs in racesetups:
        if rs.created > timezone.now() - datetime.timedelta(days=5):
            full_title = "☆" + rs.title
            we_have_new_tracks = True
        else:
            full_title = rs.title

        if len(full_title) > (MAX_LEN):
            title = full_title[:MAX_LEN] + '…'
        else:
            title = full_title
        details = utils.DetailVotes(rs.numhates, rs.numdislikes,
                                    rs.numlikes, rs.numloves)
        barchart = bars(rs.numhates, rs.numdislikes, rs.numlikes, rs.numloves,
                        max_votes_for_racesetup)
        smiley, score = details.smiley

        rslist.append(('`{id:4d}` `{title:' + str(MAX_LEN) +
                       '}` `{barchart}`{smiley}').format(
            id=rs.id, title=title, smiley=smiley, score=score,
                           barchart=barchart))

    # make multiple embeds if rslist is too long
    if len(rslist) > MAX_LINES_PER_EMBED - 1:
        partialembed = discord.Embed()
        partialembed.title = embed.title
        partialdesc = description
        for x in range(MAX_LINES_PER_EMBED - 1):
            partialdesc += rslist.pop(0) + '\n'
        while rslist:
            partialembed.description = partialdesc[:-1]
            await ctx.send(embed=partialembed)
            partialembed = discord.Embed()
            partialdesc = ''
            for x in range(MAX_LINES_PER_EMBED):
                try:
                    partialdesc += rslist.pop(0) + '\n'
                except IndexError:
                    pass
        embed.title = ''
        embed.description = partialdesc[:-1]
    else:
        description += '\n'.join(rslist)
        embed.description = description

    if we_have_new_tracks:
        append_footer_text = ('\nCombos with a "☆" have been added '
                              'in the last 5 days.')
    else:
        append_footer_text = ''
    embed.set_footer(text=''
                     'For more info about a combo use `info ID`.\n'
                     'Start a combo on the server now with `append ID`.\n'
                     '"HDLL" = number of hates / dislikes / likes / loves.'
                     + append_footer_text)
    await ctx.send(embed=embed)


class _PseudoRaceQueue:
    def __init__(self, setup):
        self.setup = setup


def _queueembed(racesetup_list=None):
    MAX_LEN = 32
    if racesetup_list:
        result = [_PseudoRaceQueue(rs) for rs in racesetup_list]
    else:
        result = RaceQueue.objects.all().order_by('index')
    embed = discord.Embed()
    embed.title = '**Upcoming combos:**'
    if result:
        rslist = []
        description = ("` ID` `{0:" + str(MAX_LEN) + "}`").format('Title') + \
            " `Downloads`\n"
        for rq in result:
            rs = rq.setup
            if len(rs.title) > MAX_LEN:
                title = rs.title[:MAX_LEN - 1] + '…'
            else:
                title = rs.title

            line = ('`{pk:3}` `{title:' + str(MAX_LEN) + '}` '
                    ).format(pk=rs.pk, title=title)
            if rs.car_download_url:
                line += '[`car`]({0}) '.format(rs.car_download_url)
            else:
                line += '`---` '
            if rs.track_download_url:
                line += '[`track`]({0})'.format(rs.track_download_url)
            else:
                line += '`-----`'
            rslist.append(line)
        description += '\n'.join(rslist)
        embed.description = description
        embed.set_footer(
            text='For more information about a combo use `info ID`.')
    else:
        embed.description = ('The queue is empty, therefore a random combo '
                             'will be used for the next round.')
    return embed


@bot.command()
@commands.check(is_writeable_channel)
async def downloads(ctx, *, ids: str):
    """Show download infos for given racesetup ids

    Example: downloads 14 15 16"""
    try:
        idlist = [int(x) for x in ids.split(' ')]
    except Exception:
        await ctx.send(embed=error(
            "You must use numbers separated by spaces."))
        return
    try:
        objs = [RaceSetup.objects.get(pk=x) for x in idlist]
    except Exception:
        await ctx.send(embed=error(
            "One or more of the ids could not be found. Aborting."))
        return

    if not objs:
        await ctx.send(embed=error(
            "I did not find anything to add to the playlist. Aborting."))
        return

    embed = _queueembed(objs)
    embed.title = ""
    embed.set_footer(text='')
    await ctx.send(embed=embed)


@bot.command()
@commands.check(is_writeable_channel)
async def append(ctx, id: int):
    """Appends a combo to the queue

    Puts the combo with the specified id (as a number which you can find out
    using the 'list' command) to the end of the queue.

    Example: append 28
    """
    try:
        rs = RaceSetup.objects.get(pk=id)
    except Exception:
        await ctx.send(embed=error(
            "Sorry, I could not find a combo with that ID."))
        return
    queue_length = RaceQueue.objects.all().count()
    people_on_server = _serverinfo()['clients']
    if people_on_server in (0, '0') and queue_length == 0:
        rq = RaceQueue(setup=rs, index=1)
        rq.save()
        _restart_acserver()
        embed = discord.Embed()
        embed.title = ("You're lucky! Nobody was on the server, "
                       "so I restarted it with your combo. "
                       "Join now and have fun!")
    else:
        max_index = 0
        if queue_length:
            max_index = RaceQueue.objects.all().order_by('-index')[0].index
        rq = RaceQueue(setup=rs, index=max_index + 1)
        rq.save()
        embed = _queueembed()
        embed.title = 'The combo has been appended. Here is the current queue.'
    await ctx.send(embed=embed)


@bot.command()
@commands.check(is_writeable_channel)
@commands.check(is_elevated_role)
async def insert(ctx, id: int):
    """Inserts a combo into the queue

    Puts the combo with the specified id (as a number which you can find out
    using the 'list' command) to the start of the queue, so it will be used
    right after the currently running round.

    Example: insert 28
    """
    try:
        rs = RaceSetup.objects.get(pk=id)
    except Exception:
        await ctx.send(embed=error(
            "Sorry, I could not find a combo with that ID."))
        return
    queue_length = RaceQueue.objects.all().count()
    new_index = 1
    if queue_length:
        for rq in RaceQueue.objects.all():
            rq.index = rq.index + 1
            rq.save()
    rq = RaceQueue(setup=rs, index=new_index)
    rq.save()
    embed = _queueembed()
    embed.title = 'The combo has been inserted. Here is the current queue.'
    await ctx.send(embed=embed)


@bot.command()
@commands.check(is_writeable_channel)
@commands.check(is_elevated_role)
async def clear(ctx):
    """Clears the queue

    Deletes all rounds waiting in the queue. The currently running round
    continues until finished, and after that a new round with a
    random combo will be started. (As long as the queue stays empty)
    """
    RaceQueue.objects.all().delete()
    embed = discord.Embed(color=0x00ff00)
    embed.title = "The queue has been emptied."
    await ctx.send(embed=embed)
    return


@bot.command()
@commands.check(is_writeable_channel)
@commands.check(is_elevated_role)
async def next(ctx):
    """Immediately starts next round

    Aborts the current round and immediately starts the next one in the
    queue, if there are combos waiting. Otherwise starts a random combo."""
    _restart_acserver()
    embed = discord.Embed(color=0x00ff00)
    embed.title = ("The current round has been aborted "
                   "and the next one started.")
    await ctx.send(embed=embed)
    return


def _restart_acserver():
    subprocess.run("sudo /usr/bin/systemctl restart acserver.service".split())
    return


@bot.command()
@commands.check(is_writeable_channel)
@commands.check(is_elevated_role)
async def playlist(ctx, *, ids: str):
    """Immediately starts a playlist

    Aborts the current round, clears the queue, and adds the combos given by id
    to the queue. Useful when starting a playlist with friends.

    Example: playlist 14 15 16"""
    try:
        idlist = [int(x) for x in ids.split(' ')]
    except Exception:
        await ctx.send(embed=error(
            "You must use numbers separated by spaces."))
        return
    try:
        objs = [RaceSetup.objects.get(pk=x) for x in idlist]
    except Exception:
        await ctx.send(embed=error(
            "One or more of the ids could not be found. Aborting."))
        return

    if not objs:
        await ctx.send(embed=error(
            "I did not find anything to add to the playlist. Aborting."))
        return

    RaceQueue.objects.all().delete()
    for idx, obj in enumerate(objs):
        rq = RaceQueue(setup=obj, index=idx + 1)
        rq.save()

    embed = _queueembed()
    embed.title = "Your playlist has started. Good luck have fun!"
    subprocess.run("sudo /usr/bin/systemctl restart acserver.service".split())
    await ctx.send(embed=embed)


@bot.command()
@commands.check(is_writeable_channel)
async def info(ctx, id: int):
    """Shows more info about a combo"""
    await ctx.send(embed=_infoembed(id))


@bot.command()
@commands.check(is_writeable_channel)
async def love(ctx, id: int):
    """User loves the combo by ID"""
    embed = _vote(ctx, id, 3)
    await ctx.send(embed=embed)
    return


@bot.command()
@commands.check(is_writeable_channel)
async def like(ctx, id: int):
    """User likes the combo by ID"""
    embed = _vote(ctx, id, 1)
    await ctx.send(embed=embed)
    return


@bot.command()
@commands.check(is_writeable_channel)
async def dislike(ctx, id: int):
    """User dislikes the combo by ID"""
    embed = _vote(ctx, id, -1)
    await ctx.send(embed=embed)
    return


@bot.command()
@commands.check(is_writeable_channel)
async def hate(ctx, id: int):
    """User hates the combo by ID"""
    embed = _vote(ctx, id, -3)
    await ctx.send(embed=embed)
    return


def _votedetails(rs_id):
    rs = RaceSetup.objects.filter(pk=rs_id).annotate(
        numhates=Count(Case(When(
            vote__value=-3, then=1), output_field=IntegerField())),
        numdislikes=Count(Case(When(
            vote__value=-1, then=1), output_field=IntegerField())),
        numlikes=Count(Case(When(
            vote__value=1, then=1), output_field=IntegerField())),
        numloves=Count(Case(When(
            vote__value=3, then=1), output_field=IntegerField())),
    )[0]
    return (rs.numhates, rs.numdislikes, rs.numlikes, rs.numloves)


def _vote(ctx, rs_id, value):
    try:
        rs = RaceSetup.objects.get(pk=rs_id)
    except Exception:
        return error("Sorry, I could not find a combo with that ID.")
    vote, created = Vote.objects.get_or_create(
        racesetup=rs,
        discorduser='{0}#{1}'.format(ctx.author.name,
                                     ctx.author.discriminator),
        defaults={'value': value})
    vote.value = value
    vote.save()
    embed = discord.Embed()
    if created:
        embed.title = "Your vote has been saved."
    else:
        embed.title = "Your vote has been changed."

    smiley, mean = utils.DetailVotes(*_votedetails(rs_id)).smiley
    embed.description = \
        'The combo "{0}" has now a mean score of {1:1.1f} {2}.'.format(
            rs.title,
            mean,
            smiley
        )

    return embed


@bot.command()
@commands.check(is_writeable_channel)
async def help(ctx):
    helptext = '''\
All commands to set up "rounds" of car/track combos for hosting a couple of races with friends.
Each round consists of 10min practice and 10min race.
Currently running combo, waiting queue and link to join are in <#814881913658671185>

**__Commands for people with `@AFTuesdays Organizer` role only__**
next
  Immediately starts next round
playlist
  Immediately starts a playlist (`playlist ID ID ID`)
clear
  Clears the queue
insert
  Inserts a combo at the beginning of the queue (`insert ID`)

**__Commands usable by everyone__**
**list**
  Shows all car/track combos including their score (calculated by peoples' opinions)
**info**
  Shows more info about a combo (`info ID`)
**append**
  Appends a combo to the end of the queue (`append ID`). If the queue is empty and nobody is on the server, then your combo will be started instantly!
**append_extra**
  Same as `append`, but does __not__ start your combo instantly when the server is empty.
  **BUT** there are some optional parameters: `-pNN` and `-rNN` for a custom amount of minutes for `p`ractice and `r`ace. Example: `-r20` for a 20 minute long race. Max minutes are 60.
  Also use `-o` if you want open setups, so you can change it.
  Example: `append_extra 7 -p20 -r45 -o` for 20min practice, 45 min race, open setups
**love/like/dislike/hate**
  Tell the bot what you think of a combo. Example: `love 7` if you love the combo with ID 7.
  (love = +3 points, like = +1 point, dislike = -1 point, hate = -3 points)
**downloads**
  Get download links for the selected combos. Example: `downloads 7 16 60`
'''

    await ctx.send(helptext)


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
        mediantxt = '  n/a '
    try:
        stddevtxt = '{0:6.2f}'.format(statistics.stdev(dv.datadump))
    except Exception:
        stddevtxt = '  n/a '

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


def error(description):
    embed = discord.Embed()
    embed.title = "That didn't work."
    embed.description = description
    return embed


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        pass
    else:
        print('Ignoring exception in command {}:'.format(
            ctx.command), file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)


def _serverinfo():
    info = {'clients': '?', 'maxclients': '?', 'free': '?'}
    try:
        info = requests.get(
            'http://127.0.0.1:8081/INFO', timeout=1).json()
        info['free'] = info['maxclients'] - info['clients']
    except Exception:
        pass
    return info
