from django.conf import settings
from django.core.management.base import BaseCommand

from races.management.commands.botfunctions import bot


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        bot.run(settings.DISCORDTOKEN)
        print("Done.")
