import os
import pathlib

from django.conf import settings

from adhoc.raceconfigs import ServerSetup
from main.acserver import ac_run


class Tierdrop:

    def __init__(self, adhocrace):
        self.race = adhocrace

    def initialize(self):
        self.rootdir = pathlib.Path(settings.ACWRAPPEREXE).parent
        self.sessioncfgdir = self.rootdir / 'cfg'
        self.server = ServerSetup(
            os.path.join(self.sessioncfgdir, 'server_cfg.ini'),
            os.path.join(self.sessioncfgdir, 'entry_list.ini'))

    def run(self):
        """directory is prepared, all files are there etc."""
        self.initialize()
        current_round = 0
        ac_run()
        while (current_round < self.server.rounds) and \
                self.race.result_available:
            current_round += 1
            self.server
        self.server.rounds
