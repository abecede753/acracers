import asyncio

import discord
from django.conf import settings
from django.core.management.base import BaseCommand
from races.management.commands.botfunctions import (
    _infoembed, error, _queueembed)
from races.models import Race


def join_embed():
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

    def set_queue_footer(self, queueembed):
        if 'Title' in queueembed.description:
            queueembed.set_footer(text="These combos will be started in order after the current round")
        else:
            queueembed.set_footer(text='')
        return queueembed


    async def live_status(self):
        await self.wait_until_ready()
        channel = self.get_channel(settings.DISCORDLIVECHANNEL)
        current_race_id = None
        live_message = None

        # delete all messages in the channel when starting up.
        messages = await channel.history(limit=100).flatten()
        await channel.delete_messages(messages)

        # insert our two messages that always should be here.
        live_message = await channel.send(embed=error("Initializing..."))
        queueembed = self.set_queue_footer(_queueembed())
        queue_message = await channel.send(embed=queueembed)
        await channel.send(embed=join_embed())

        while not self.is_closed():
            try:
                race = Race.objects.all().order_by('-id')[0]
            except Exception:
                await live_message.edit(embed=error(
                    "There is nothing running on the server at the moment."))

            if race.pk != current_race_id:
                current_race_id = race.pk
                await live_message.edit(embed=_infoembed(race.racesetup.id))

            new_queueembed = _queueembed()
            if new_queueembed.description != queueembed.description:
                queueembed = self.set_queue_footer(new_queueembed)
                await queue_message.edit(embed=queueembed)

            await asyncio.sleep(4)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        client = LiveBot()
        client.run(settings.DISCORDLIVETOKEN)
        print("Done.")
