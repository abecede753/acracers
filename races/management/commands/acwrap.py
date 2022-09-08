from datetime import datetime
import logging
import pathlib
import random
import subprocess
import sys
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from races.models import (RaceSetup, Race, RaceQueue,
                          cleanup_RaceQueue_indices)
from races.management.commands.live_options import set_live_options


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    proc = None
    race = None

    def handle(self, *args, **kwargs):
        pass
        logger.info("starting up.")
        while True:
            self.setup_race()

            self.proc = subprocess.Popen(
                [settings.ACWRAPPEREXE, ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=pathlib.Path(settings.ACWRAPPEREXE).parent,
                encoding="utf-8"
            )
            while self.proc.poll() is None:
                self.loop()

            logger.info("server ended.")

            self.race.stdout = self.proc.stdout.read() + 'END'
            self.race.stderr = self.proc.stderr.read() + 'END'
            self.race.end_ts = datetime.now()
            self.race.delete()  # dont save these races anymore.
            time.sleep(0.2)

    def loop(self):
        time.sleep(2)
        # print(".", end=' ')
        # sys.stdout.flush()

    def setup_race(self):
        race_options = ''
        queue_length = RaceQueue.objects.all().count()
        if queue_length:
            rq = RaceQueue.objects.all().order_by('index')[0]
            print("fetching from queue...", rq)
            racesetup = rq.setup
            race_options = rq.options
            rq.delete()
            cleanup_RaceQueue_indices()
        else:
            valid_setups = RaceSetup.objects.filter(
                randomizable=True).exclude(
                tgz__isnull=True).exclude(tgz='')
            setups_count = valid_setups.count()
            race_num = random.randint(1, setups_count) - 1
            racesetup = valid_setups.order_by('id')[race_num]
        self.race = Race(racesetup=racesetup)
        self.race.save()
        self.race.racesetup.unpack_for_acserver()
        if race_options:
            set_live_options(race_options)
