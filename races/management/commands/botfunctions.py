import discord
from discord.ext import commands

from races.models import RaceSetup, RaceQueue

description = '''Here are the commands to set up "race queues" for hosting a
couple of races in order with friends.'''

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='', description=description,
                   intents=intents)


# @bot.event
# async def on_ready():
#     print('Logged in as {0}'.format(bot.user.name))


@bot.command()
async def list(ctx):
    """Show a list of all race-setups."""
    MAX_LEN = 32
    embed = discord.Embed()
    embed.title = "These are all race setups for now."
    description = "`  ID` `Name                            `\n"
    rslist = []
    for rs in RaceSetup.objects.all().order_by('title'):
        if len(rs.title) > MAX_LEN:
            title = rs.title[:MAX_LEN] + '…'
        else:
            title = rs.title
        rslist.append('`{id:4d}` `{title:32}`'.format(id=rs.id, title=title))
    description += '\n'.join(rslist)
    embed.description = description
    embed.set_footer(text='Add a race setup to the queue with '
                     '`append ID` or `insert ID`.')
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
    result = _list_queue(objects=True)
    if result:
        embed = discord.Embed(color=0x00ff00)
        embed.title = '**Upcoming race-setups:**'
        await ctx.send(embed=embed)
        for rq in result:
            embed = discord.Embed()
            # embed.title = str(rq)
            embed.set_image(url='https://acracers.com' + rq.setup.image.url)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(color=0x00ff00)
        embed.title = 'The queue is empty. Therefore a random race setup will be used next.'
        await ctx.send(embed=embed)


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
    result = _list_queue()
    await ctx.send('\n'.join(result))


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
    result = _list_queue()
    await ctx.send('\n'.join(result))


@bot.command()
async def clear(ctx):
    """Clear the race queue."""
    RaceQueue.objects.all().delete()
    embed = discord.Embed(color=0x00ff00)
    embed.title = "The queue has been emptied. A random race setup will be used next."
    await ctx.send(embed=embed)
    return


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
    embed.description = rs.description
    await ctx.send(embed=embed)


def error(description):
    embed = discord.Embed()
    embed.title = "That didn't work."
    embed.description = description
    return embed

