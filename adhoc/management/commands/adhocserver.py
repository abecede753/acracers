import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from adhoc.models import AdhocRace
from main.acserver import pause


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    proc = None
    adhocrace = None
    overrides = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.overrides = {
            'SERVER': {'HTTP_PORT': settings.ACSERVERPORT,
                       'TCP_PORT': settings.ACSERVERTCPPORT,
                       'UDP_PORT': settings.ACSERVERUDPPORT
                       }
        }
        # remove any previously crashed session
        AdhocRace.objects.filter(
            end_ts__isnull=True,
            start_ts__isnull=False).delete()

    def handle(self, *args, **kwargs):
        while True:
            while not self.race_available:
                pause()
            self.adhocrace = AdhocRace.objects.all().order_by('index')[0]
            self.adhocrace.startup(self.overrides)
            self.adhocrace.run()
            have_result = self.adhocrace.teardown()
            if not have_result:
                self.adhocrace.delete()  # no need to save an empty session.

    @property
    def race_available(self):
        return AdhocRace.objects.filter(index__gt=0).count()
