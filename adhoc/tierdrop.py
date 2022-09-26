import configparser
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
    # group by carindex
    vehiclenumbers = set(map(lambda driver: driver.car.carindex, drivers))
    groups = [[y for y in drivers if y.car.carindex == vehiclenumber]
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
            if d['TotalTime'] > 1:
                car = next(c for c in self.cars if c.model == d['CarModel'])
                drivers.append(Driver(d['DriverName'], d['DriverGuid'], car))
        self.drivers = drivers

    def advance_drivers(self):
        """better half of drivers get a slower car."""
        for d in self.drivers[:(len(self.drivers) - (len(self.drivers) // 2))]:
            d.car = self.cars[d.car.carindex + 1]

    def create_initial_entry_list_file(self):
        """since original entry_list.ini consists only of a few cars,
        build the grid with fastest car."""
        car = self.serversetup.entry_list.distinct_cars[0]  # ['CAR_0']
        cfg = configparser.RawConfigParser()
        cfg.optionxform = str
        for index in range(self.serversetup.server_cfg.max_clients):
            cfg['CAR_{0}'.format(index)] = {
                'MODEL': car.model,
                'SKIN': car.skin,
                'SPECTATOR_MODE': '0',
                'DRIVERNAME': '',
                'TEAM': '',
                'GUID': '',
                'BALLAST': '0',
                'RESTRICTOR': '0',
                'FIXED_SETUP': car.fixed_setup}
        with (self.sessioncfgdir / 'entry_list.ini').open('w') as f:
            cfg.write(f, space_around_delimiters=False)

    def run(self):
        """directory is prepared, all files are there etc."""
        self.initialize()
        current_round = 0
        self.create_initial_entry_list_file()
        ac_run()
        while (current_round < self.serversetup.rounds) and \
                self.adhocrace.result_available:
            current_round += 1
            self.get_current_drivers()
            self.advance_drivers()
            self.create_entry_list_file()
            ac_run()
