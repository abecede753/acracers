import asyncio

import discord
from django.conf import settings
from django.core.management.base import BaseCommand
from races.management.commands.botfunctions import _infoembed, error
from races.models import Race


def joinembed():
    embed = discord.Embed()
    embed.title = 'Join the fun now!'
    embed.description = '''
[`CLICK HERE to join with Content Manager`](https://acstuff.ru/s/q:race/online/join?ip=176.223.131.53&httpPort=8081)

(If you don't have Content Manager, you might try searching for "acracers" in the AC server list.)
'''
    return embed


class LiveBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_task = self.loop.create_task(self.live_status())

    async def live_status(self):
        await self.wait_until_ready()
        channel = self.get_channel(settings.DISCORDLIVECHANNEL)
        current_race_id = None
        while not self.is_closed():
            try:
                race = Race.objects.all().order_by('-id')[0]
            except Exception:
                await channel.send(embed=error(
                    "There is nothing running on the server at the moment."))

            if race.pk != current_race_id:
                current_race_id = race.pk
                messages = await channel.history(limit=100).flatten()
                await channel.delete_messages(messages)
                await channel.send(embed=_infoembed(race.racesetup.id))
                await channel.send(embed=joinembed())

            await asyncio.sleep(4)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        client = LiveBot()
        client.run(settings.DISCORDLIVETOKEN)
        print("Done.")
