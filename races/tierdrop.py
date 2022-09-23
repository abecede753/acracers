import demjson
import os
import pathlib

from django.conf import settings

from adhoc.raceconfigs import ServerSetup, Driver
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

    # only one group
    if not num_empty_groups:
        return groups.pop(0)

    # multiple groups...
    empty_group_size, extra_spots = divmod(total_empty_slots, num_empty_groups)
    result = groups.pop(0)
    for group in groups:
        if extra_spots > 0:
            result += [None] * (empty_group_size + 1)
            extra_spots -= 1
        else:
            result += [None] * (empty_group_size)
        result += group
    return result


class Tierdrop:

    def __init__(self, adhocrace):
        self.adhocrace = adhocrace

    def initialize(self):
        self.rootdir = pathlib.Path(settings.ACWRAPPEREXE).parent
        self.sessioncfgdir = self.rootdir / 'cfg'
        self.serversetup = ServerSetup(
            os.path.join(self.sessioncfgdir, 'server_cfg.ini'),
            os.path.join(self.sessioncfgdir, 'entry_list.ini'))
        self.cars = self.serversetup.entry_list.distinct_cars

    def get_current_drivers(self):
        """read results/RACE.json and create driverlist in order
        from this race."""
        resultfiles = sorted(
            [x for x in (self.rootdir / 'results').glob('*RACE*json')])
        if not resultfiles:
            return []
        result = demjson.decode(resultfiles[-1].open().read())
        drivers = []
        for d in result['Result']:
            car = next(c for c in self.cars if c.model == d['CarModel'])
            drivers.append(Driver(d['DriverName'], d['DriverGuid'], car))
        return drivers

    def advance_drivers(self):
        """better half of drivers get a slower car."""
        for d in self.drivers[:(len(self.drivers) - (len(self.drivers) // 2))]:
            d.car = self.cars[d.car.index + 1]

    def run(self):
        """directory is prepared, all files are there etc."""
        self.initialize()
        current_round = 0
        raw_input("ACRUN")  # ac_run()
        while (current_round < self.serversetup.rounds) and \
                self.adhocrace.result_available:
            current_round += 1
            self.drivers = self.get_current_drivers()
            self.advance_drivers()
