import logging
import pathlib
import psutil
import subprocess
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from adhoc.models import cleanup_AdhocRace_indices, AdhocRace


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
        AdhocRace.objects.filter(end_ts__isnull=True,
                                 start_ts__isnull=False).delete()

    def handle(self, *args, **kwargs):
        pass
        logger.info("starting up.")
        while True:
            if not self.setup_race():
                self.pause()
                continue
            print("running", self.race)

            self.proc = subprocess.Popen(
                [settings.ACWRAPPEREXE, ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=pathlib.Path(settings.ACWRAPPEREXE).parent,
                encoding="utf-8"
            )
            pidfile = pathlib.Path(settings.ACWRAPPEREXE).parent / 'pidfile'
            with pidfile.open(mode="w", encoding="utf-8") as f:
                f.write(str(self.proc.pid))
            panictimeout = 0
            while self.proc.poll() is None:
                self.pause()
                if 'acServer' not in [x.name() for x in psutil.process_iter()]:
                    panictimeout += 1
                else:
                    panictimeout = 0
                if panictimeout > 2:
                    print("panic! killing acwrapper.")
                    try:
                        subprocess.Popen.kill(self.proc)
                    except Exception:
                        print("EXTRAPANIC?")
                    self.pause()

            pidfile.unlink()
            print("server ended.")
            have_result = self.race.teardown()
            if not have_result:
                print("deleting - no results.")
                self.race.delete()

    def pause(self):
        time.sleep(1)

    def setup_race(self):
        if not AdhocRace.objects.filter(index__gt=0).count():
            return False
        self.race = AdhocRace.objects.all().order_by('index')[0]
        self.race.startup(self.overrides)
        return True
