import pathlib
import shutil
from unittest import TestCase

from adhoc.models import AdhocRace
from adhoc.raceconfigs import Car, Driver
from adhoc.tierdrop import build_grid, Tierdrop
from django.conf import settings


class BuildGridTest(TestCase):
    def test_groups(self):

        # 3 drivers in 1 group
        drivers = [Driver('a', '0001', Car(0, 'audi', 'white', 1)),
                   Driver('b', '0002', Car(0, 'audi', 'white', 1)),
                   Driver('c', '0003', Car(0, 'audi', 'white', 1)),
                   ]
        grid = build_grid(drivers, 4)
        self.assertEqual(
            str(grid),
            "[a, b, c]"
        )

        # 4 drivers in 2 groups
        drivers += [Driver('d', '0004', Car(1, 'bmw', 'black', 1))]
        grid = build_grid(drivers, 10)
        self.assertEqual(
            str(grid),
            '[d, None, None, None, None, None, None, a, b, c]'
        )

        # 6 drivers in 3 groups
        drivers += [Driver('e', '0005', Car(2, 'citroen', 'green', 1))]
        drivers += [Driver('f', '0006', Car(2, 'citroen', 'green', 1))]
        grid = build_grid(drivers, 10)
        self.assertEqual(
            str(grid),
            '[e, f, None, None, d, None, None, a, b, c]')
        grid = build_grid(drivers, 11)
        self.assertEqual(
            str(grid),
            '[e, f, None, None, None, d, None, None, a, b, c]')

        # add another driver for group "audi" after other groups
        # and see whether they get pushed into their group correctly
        drivers += Driver('g', '0007', Car(0, 'audi', 'white', 1)),
        grid = build_grid(drivers, 11)
        self.assertEqual(
            str(grid),
            '[e, f, None, None, d, None, None, a, b, c, g]')
        grid = build_grid(drivers, 7)
        self.assertEqual(
            str(grid),
            '[e, f, d, a, b, c, g]')
        grid = build_grid(drivers, 8)
        self.assertEqual(
            str(grid),
            '[e, f, None, d, a, b, c, g]')

        # 10 drivers in 5 groups...
        drivers += Driver('h', '0008', Car(3, 'datsun', 'yellow', 1)),
        drivers += Driver('i', '0009', Car(3, 'datsun', 'yellow', 1)),
        drivers += Driver('j', '0010', Car(4, 'equus', 'red', 1)),
        lengrid = 20
        desired = [
            (10, '[j, h, i, e, f, d, a, b, c, g]'),
            (11, '[j, None, h, i, e, f, d, a, b, c, g]'),
            (15, '[j, None, None, h, i, None, e, f, None, d, None, a, b, '
             'c, g]'),
        ]

        for idx, lengrid in enumerate([10, 11, 15]):
            grid = build_grid(drivers, lengrid)
            self.assertEqual(len(grid), desired[idx][0])
        self.assertEqual(str(grid), desired[idx][1])

    def init_acdirectory(self):
        """fill acserver directory with stuff."""
        sessionrootdir = pathlib.Path(settings.ACWRAPPEREXE).parent
        shutil.rmtree(sessionrootdir)
        sessioncfgdir = sessionrootdir / 'cfg'
        sessioncfgdir.mkdir(parents=True, exist_ok=True)
        testfilesdir = pathlib.Path(__file__).parent / 'testfiles'
        for fname in ('entry_list.ini', 'server_cfg.ini'):
            shutil.copyfile(testfilesdir / fname, sessioncfgdir / fname)
        return sessionrootdir

    def test_initial_grid(self):
        rootdir = self.init_acdirectory()
        adhocrace = AdhocRace()
        td = Tierdrop(adhocrace)
        td.initialize()
        td.create_initial_entry_list_file()

        content = (rootdir / 'cfg' / 'entry_list.ini').open().read()
        assert '[CAR_1]' in content
        assert '[CAR_23]' in content
        assert '[CAR_24]' not in content
        assert 'lotus_2_eleven_gt4' in content

    def test_second_grid(self):
        resultsdir = self.init_acdirectory() / 'results'
        resultsdir.mkdir(parents=True, exist_ok=True)
        adhocrace = AdhocRace()
        td = Tierdrop(adhocrace)
        testfilesdir = pathlib.Path(__file__).parent / 'testfiles'
        shutil.copyfile(testfilesdir / '1_RACE.json',
                        resultsdir / '1_RACE.json')
        td.initialize()
        td.get_current_drivers()
        assert [(x.name, x.car.model) for x in td.drivers] == \
               [('u3', 'lotus_2_eleven_gt4'),
                ('abe', 'lotus_2_eleven_gt4'),
                ('u1', 'lotus_2_eleven_gt4')]
        td.advance_drivers()
        assert [(x.name, x.car.model) for x in td.drivers] == \
               [('u3', 'lotus_exige_v6_cup'),
                ('abe', 'lotus_exige_v6_cup'),
                ('u1', 'lotus_2_eleven_gt4')]
        pass
