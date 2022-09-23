from unittest import TestCase
from adhoc.raceconfigs import Car, Driver
from races.tierdrop import build_grid


class BuildGridTest(TestCase):
    def test_onegroup(self):
        drivers = [Driver('a', '0001', Car(0, 'audi', 'white', 1)),
                   Driver('b', '0002', Car(0, 'audi', 'white', 1)),
                   Driver('c', '0003', Car(0, 'audi', 'white', 1)),
                   ]
        grid = build_grid(drivers, 4)
        self.assertEqual(
            str(grid),
            "[a, b, c]"
        )
        drivers += [Driver('d', '0004', Car(1, 'bmw', 'black', 1))]
        grid = build_grid(drivers, 10)
        self.assertEqual(
            str(grid),
            '[a, b, c, None, None, None, None, None, None, d]'
        )
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
