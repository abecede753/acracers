from unittest import TestCase
from adhoc.raceconfigs import Car, Driver
from races.tierdrop import build_grid


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
(15, '[a, b, c, g, None, None, d, None, e, f, None, h, i, None, j]'),
(16, '[a, b, c, g, None, None, d, None, None, e, f, None, h, i, None, j]'),
(17, '[a, b, c, g, None, None, d, None, None, e, f, None, None, h, i, None, j]'),
(18, '[a, b, c, g, None, None, d, None, None, e, f, None, None, h, i, None, None, j]'),
(19, '[a, b, c, g, None, None, None, d, None, None, e, f, None, None, h, i, None, None, j]')
        ]
        for idx, lengrid in enumerate((10, 11, 12, 13, 14, 15, 16, 17, 18, 19)):
            grid = build_grid(drivers, lengrid)
            self.assertEqual(len(grid), desired[idx][0])
        self.assertEqual(str(grid), desired[idx][1])
