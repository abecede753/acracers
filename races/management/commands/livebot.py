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
    embed.description = (
        "[`CLICK HERE to join with Content Manager`]"
        "(https://acstuff.ru/s/q:race/online/join?"
        "ip=176.223.131.53&httpPort=8081)\n\n"
        "(If you don't have Content Manager, you might "
        "try searching for 'acracers' in the AC server list.)"
    )
    return embed


class LiveBot(discord.Client):

    channels = ()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.live_messages = []
        self.queue_messages = []
        self.bg_task = self.loop.create_task(self.live_status())

    def _set_queue_footer(self, queueembed):
        """Set a different footer text depending on a full or
        empty queue."""
        if 'Title' in queueembed.description:
            text = ("These combos will be started in order "
                    "after the current round")
        else:
            text = ""
        queueembed.set_footer(text=text)
        return queueembed

    async def live_status(self):
        await self.wait_until_ready()
        self.channels = [self.get_channel(c) for c in
                         settings.DISCORDLIVECHANNELS]
        current_race_id = None

        # delete all messages in the channel when starting up.
        for channel in self.channels:
            messages = await channel.history(limit=100).flatten()
            await channel.delete_messages(messages)

        # insert our two messages that always should be here.
        for channel in self.channels:
            livemsg = await channel.send(embed=error("Initializing..."))
            self.live_messages.append(livemsg)

        queueembed = self._set_queue_footer(_queueembed())
        for channel in self.channels:
            queuemsg = await channel.send(embed=queueembed)
            self.queue_messages.append(queuemsg)

        for channel in self.channels:
            await channel.send(embed=join_embed())

        while not self.is_closed():
            try:
                race = Race.objects.all().order_by('-id')[0]
            except Exception:
                await self.broadcast(
                    embed=error("There is nothing running on the "
                                "server at the moment."),
                    messages=self.live_messages
                )

            if race.pk != current_race_id:
                current_race_id = race.pk
                await self.broadcast(embed=_infoembed(race.racesetup.id),
                                     messages=self.live_messages)

            new_queueembed = _queueembed()
            if new_queueembed.description != queueembed.description:
                queueembed = self._set_queue_footer(new_queueembed)
                await self.broadcast(embed=queueembed,
                                     messages=self.queue_messages)

            await asyncio.sleep(4)

    async def broadcast(self, embed, messages):
        for message in messages:
            await message.edit(embed=embed)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        client = LiveBot()
        client.run(settings.DISCORDLIVETOKEN)
        print("Done.")
