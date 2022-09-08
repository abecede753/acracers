CHARS = '▁▂▃▄▅▆▇█'


def _bar(num, total):
    index = round(100 / total * num / 12.5)
    index = min(index, 7)
    index = max(index, 0)
    return CHARS[index]


def bars(loves, likes, dislikes, hates, total=None):
    if total is None:
        total = loves + likes + dislikes + hates

    return (_bar(loves, total) + _bar(likes, total) +
            _bar(dislikes, total) + _bar(hates, total))


if __name__ == "__main__":
    for items in (
        [2, 4, 6, 1],
        [0, 2, 3, 8, 16],
        [0, 2, 3, 8, 20],
        [0, 2, 3, 8, 80],
    ):
        print(bars(*items))

