import subprocess

import discord
from discord.ext import commands

from races.models import RaceSetup, RaceQueue

description = ('Here are the commands to set up "rounds" of car/track combos '
               'for hosting a couple of races with friends.\nEach round '
               'consists of 10min qualifying, 10min race one, 10min race two '
               'with inverted starting grid.')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='', description=description,
                   intents=intents)


@bot.command()
async def list(ctx):
    """Shows all car/track combos

    You can then add a combo (using its ID) to the queue for having fun with your friends.
    """
    MAX_LEN = 40
    embed = discord.Embed()
    embed.title = "These are all combos for now."
    description = ("`  ID` `{0:" + str(MAX_LEN) + "}`\n").format('Title')
    rslist = []
    for rs in RaceSetup.objects.all().order_by('title'):
        if len(rs.title) > MAX_LEN:
            title = rs.title[:MAX_LEN - 1] + '…'
        else:
            title = rs.title
        rslist.append(('`{id:4d}` `{title:' + str(MAX_LEN) + '}`').format(
            id=rs.id, title=title))
    description += '\n'.join(rslist)
    embed.description = description
    embed.set_footer(text='Add a combo to the queue with '
                     '`append ID` or `insert ID`.\n'
                     'For more information about a combo use `info ID`.')
    await ctx.send(embed=embed)


def _list_queue(objects=False):
    result = []
    for rq in RaceQueue.objects.all().order_by('index'):
        if objects:
            result.append(rq)
        else:
            result.append('{0}'.format(rq))
    return result


@bot.command()
async def queue(ctx):
    """Shows the current queue of rounds

    When you or someone else "appends" or "inserts" a combo, then this will be
    added as a round to the queue. Each round usually consists of qualifying, race 1
    and race 2 (with reversed grid).
    """
    await ctx.send(embed=_queueembed())


def _queueembed():
    MAX_LEN = 32
    result = _list_queue(objects=True)
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
        embed.description = 'The queue is empty, therefore a random combo will be used for the next round.'
    return embed


@bot.command()
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
    max_index = 0
    if queue_length:
        max_index = RaceQueue.objects.all().order_by('-index')[0].index
    rq = RaceQueue(setup=rs, index=max_index + 1)
    rq.save()
    embed = _queueembed()
    embed.title = 'The combo has been appended. Here is the current queue.'
    await ctx.send(embed=embed)


@bot.command()
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
async def next(ctx):
    """Immediately starts next round

    Aborts the current round and immediately starts the next one in the
    queue, if there are combos waiting. Otherwise starts a random combo."""
    subprocess.run("sudo /usr/bin/systemctl restart acserver.service".split())
    embed = discord.Embed(color=0x00ff00)
    embed.title = "The current round has been aborted and the next one started."
    await ctx.send(embed=embed)
    return


@bot.command()
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
async def info(ctx, id: int):
    """Shows more info about a combo
    
    Use 'info ID', where ID is the number you get when you 'list' all race setups."""
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


# STUFF FOR NEXT IMPLEMENTATIONS (roles and such)
# @bot.command()
# async def dbg(ctx, x: str):
#     """Clear the race queue."""
#     embed = discord.Embed(color=0x00ff00)
#     embed.title = "In debug mode..."
#     await ctx.send(embed=embed)
#     """
# ctx.message.channel.name
# 'now-playing'
# 
# [x.name for x in ctx.author.roles]
# ['@everyone', 'Member', 'Early Bird']
# 
#     """
#     embed = discord.Embed(color=0x00ff00)
#     embed.title = "Continuing."
#     await ctx.send(embed=embed)
