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
            '[a, b, c, None, None, None, None, None, None, d]'
        )

        # 6 drivers in 3 groups
        drivers += [Driver('e', '0005', Car(2, 'citroen', 'green', 1))]
        drivers += [Driver('f', '0006', Car(2, 'citroen', 'green', 1))]
        grid = build_grid(drivers, 10)
        self.assertEqual(
            str(grid),
            '[a, b, c, None, None, d, None, None, e, f]')
        grid = build_grid(drivers, 11)
        self.assertEqual(
            str(grid),
            '[a, b, c, None, None, None, d, None, None, e, f]')

        # add another driver for group "audi" after other groups
        # and see whether they get pushed into their group correctly
        drivers += Driver('g', '0007', Car(0, 'audi', 'white', 1)),
        grid = build_grid(drivers, 11)
        self.assertEqual(
            str(grid),
            '[a, b, c, g, None, None, d, None, None, e, f]')
        grid = build_grid(drivers, 7)
        self.assertEqual(
            str(grid),
            '[a, b, c, g, d, e, f]')
        grid = build_grid(drivers, 8)
        self.assertEqual(
            str(grid),
            '[a, b, c, g, None, d, e, f]')

        # 10 drivers in 5 groups...
        drivers += Driver('h', '0008', Car(3, 'datsun', 'yellow', 1)),
        drivers += Driver('i', '0009', Car(3, 'datsun', 'yellow', 1)),
        drivers += Driver('j', '0010', Car(4, 'equus', 'red', 1)),
        lengrid = 20
        desired = [
            (10, '[a, b, c, g, d, e, f, h, i, j]'),
            (11, '[a, b, c, g, None, d, e, f, h, i, j]'),
            (12, '[a, b, c, g, None, d, None, e, f, h, i, j]'),
            (13, '[a, b, c, g, None, d, None, e, f, None, h, i, j]'),
            (14, '[a, b, c, g, None, d, None, e, f, None, h, i, None, j]'),
            (15, '[a, b, c, g, None, None, d, None, e, f, None, h, i, None, '
             'j]'),
            (16, '[a, b, c, g, None, None, d, None, None, e, f, None, h, i, '
             'None, j]'),
            (17, '[a, b, c, g, None, None, d, None, None, e, f, None, None, '
             'h, i, None, j]'),
            (18, '[a, b, c, g, None, None, d, None, None, e, f, None, None, '
             'h, i, None, None, j]'),
            (19, '[a, b, c, g, None, None, None, d, None, None, e, f, None, '
             'None, h, i, None, None, j]')]

        for idx, lengrid in enumerate(range(10, 20)):
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
        td.create_initial_entry_list()

        content = (rootdir / 'cfg' / 'entry_list.ini').open().read()
        assert '[CAR_1]' in content
        assert '[CAR_23]' in content
        assert '[CAR_24]' not in content
        assert 'lotus_2_eleven_gt4' in content



