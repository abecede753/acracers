import subprocess

import discord
from discord.ext import commands

from races.models import RaceSetup, RaceQueue

description = '''Here are the commands to set up "race queues" for hosting a
couple of races in order with friends.'''

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='', description=description,
                   intents=intents)


@bot.command()
async def list(ctx):
    """Show a list of all race-setups."""
    MAX_LEN = 40
    embed = discord.Embed()
    embed.title = "These are all race setups for now."
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
    embed.set_footer(text='Add a race setup to the queue with '
                     '`append ID` or `insert ID`.\n'
                     'For more information about a race setup use `info ID`.')
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
    """Show the current race queue."""
    await ctx.send(embed=_queueembed())


def _queueembed():
    MAX_LEN = 32
    result = _list_queue(objects=True)
    embed = discord.Embed()
    embed.title = '**Upcoming race-setups:**'
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

            line = ('`{pk:3}` `{title:' + str(MAX_LEN) + '}`'
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
            text='For more information about a race use `info ID`.')
    else:
        embed = discord.Embed(color=0x00ff00)
        embed.title = 'The queue is empty. ' + \
            'Therefore a random race setup will be used next.'
    return embed


@bot.command()
async def append(ctx, id: int):
    """Append a race-setup to the end of the race queue."""
    try:
        rs = RaceSetup.objects.get(pk=id)
    except Exception:
        await ctx.send(embed=error(
            "Sorry, I could not find a race setup with that ID."))
        return
    queue_length = RaceQueue.objects.all().count()
    max_index = 0
    if queue_length:
        max_index = RaceQueue.objects.all().order_by('-index')[0].index
    rq = RaceQueue(setup=rs, index=max_index + 1)
    rq.save()
    embed = _queueembed()
    embed.title = 'The race setup has been appended. Here is the current queue.'
    await ctx.send(embed=embed)


@bot.command()
async def insert(ctx, id: int):
    """Insert a race-setup at the start of the race queue."""
    try:
        rs = RaceSetup.objects.get(pk=id)
    except Exception:
        await ctx.send(embed=error(
            "Sorry, I could not find a race setup with that ID."))
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
    embed.title = 'The race setup has been inserted. Here is the current queue.'
    await ctx.send(embed=embed)


@bot.command()
async def clear(ctx):
    """Clear the race queue."""
    RaceQueue.objects.all().delete()
    embed = discord.Embed(color=0x00ff00)
    embed.title = "The queue has been emptied. " + \
        "A random race setup will be used next."
    await ctx.send(embed=embed)
    return


@bot.command()
async def next(ctx):
    """Abort current race and start the next one."""
    subprocess.run("sudo /usr/bin/systemctl restart acserver.service".split())
    embed = discord.Embed(color=0x00ff00)
    embed.title = "The current race has been aborted and the next one started."
    await ctx.send(embed=embed)
    return


@bot.command()
async def playlist(ctx, *, ids: str):
    """Immediately start a playlist with the tracks given by id.
    Example: `playlist 14 15 16`"""
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
    """Get more information about a race setup. use 'info ID', where ID is the
    number you get when you 'list' all race setups."""
    try:
        rs = RaceSetup.objects.get(pk=id)
    except Exception:
        await ctx.send(embed=error(
            "Sorry, I could not find a race setup with that ID."))
        return
    embed = discord.Embed()
    embed.title = rs.title
    embed.set_image(url='https://acracers.com' + rs.image.url)
    desc = rs.description
    if rs.car_download_url:
        desc += '\n\nCar download: {0}'.format(rs.car_download_url)
    if rs.track_download_url:
        desc += '\n\nTrack download: {0}'.format(rs.track_download_url)
    embed.description = desc
    await ctx.send(embed=embed)


def error(description):
    embed = discord.Embed()
    embed.title = "That didn't work."
    embed.description = description
    return embed


# STUFF FOR NEXT IMPLEMENTATIONS (roles and such)
@bot.command()
async def dbg(ctx, x: str):
    """Clear the race queue."""
    embed = discord.Embed(color=0x00ff00)
    embed.title = "In debug mode..."
    await ctx.send(embed=embed)
    """
ctx.message.channel.name
'now-playing'

[x.name for x in ctx.author.roles]
['@everyone', 'Member', 'Early Bird']

    """
    embed = discord.Embed(color=0x00ff00)
    embed.title = "Continuing."
    await ctx.send(embed=embed)
