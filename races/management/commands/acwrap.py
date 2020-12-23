from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import logging
import pathlib
import random
import subprocess
import sys
import threading
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from races.models import RaceSetup, Race


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
            self.race.save()
            time.sleep(0.2)

    def loop(self):
        time.sleep(2)
        print(".", end=' ')
        sys.stdout.flush()

    def setup_race(self):
        Race.objects.all().update(end_ts=datetime.now())
        valid_setups = RaceSetup.objects.exclude(
            tgz__isnull=True).exclude(tgz='').exclude(id__lt=13)
        setups_count = valid_setups.count()
        race_num = random.randint(1, setups_count) - 1
        racesetup = valid_setups.order_by('id')[race_num]
        self.race = Race(racesetup=racesetup)
        self.race.save()
        self.race.racesetup.unpack_for_acserver()
