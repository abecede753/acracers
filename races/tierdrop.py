import os
import pathlib

from django.conf import settings

from adhoc.raceconfigs import ServerSetup
from main.acserver import ac_run


def build_grid(drivers, max_clients):
    """drivers is a list in this format:
       ordered by last race finishing position. cars must be the cars for the
       next race.
    """
    # group by carnumber
    vehiclenumbers = set(map(lambda driver: driver.car.carnumber, drivers))
    groups = [[y for y in drivers if y.car.carnumber == vehiclenumber]
              for vehiclenumber in vehiclenumbers]

    num_empty_groups = len(groups) - 1
    total_empty_slots = max_clients - len(drivers)
    if not num_empty_groups:  # only one vehiclenumber in the race
        return groups.pop(0)

    empty_group_size, extra_spots = divmod(total_empty_slots, num_empty_groups)
    result = groups.pop(0)
    first_time = True
    for group in groups:
        if first_time:
            result += [None] * (empty_group_size + extra_spots)
            first_time = False
        else:
            result += [None] * empty_group_size
        result += group
    return result


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
