import logging
import pathlib

from django.conf import settings
from django.core.management.base import BaseCommand

from adhoc.models import AdhocRace
from main.acserver import ac_run, pause


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    proc = None
    race = None
    overrides = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.overrides = {
            'SERVER': {'HTTP_PORT': 8081,
                       'TCP_PORT': 9001,
                       'UDP_PORT': 9001
                       }
        }
        # remove any previously crashed session
        AdhocRace.objects.filter(
            end_ts__isnull=True,
            start_ts__isnull=False).delete()

    def handle(self, *args, **kwargs):
        while True:
            if not self.setup_race():
                pause()
                continue
            self.race.run()
            result_available = self.race.teardown()
            if not result_available:
                self.race.delete()  # no need to save an empty session.

    def setup_race(self):
        if not AdhocRace.objects.filter(index__gt=0).count():
            return False
        self.race = AdhocRace.objects.all().order_by('index')[0]
        self.race.startup(self.overrides)
        return True
