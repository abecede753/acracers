import statistics


class DetailVotes:
    hates = 0
    likes = 0
    dislikes = 0
    loves = 0
    unicodebars = ' ▏▎▍▌▋▊▉█'
    smileys = '😣🙁🙂😊'

    def __init__(self, hates=0, dislikes=0, likes=0, loves=0):
        self.hates = hates
        self.likes = likes
        self.dislikes = dislikes
        self.loves = loves

    def sixteenths(self, what):
        the_max = max(self.hates, self.likes, self.dislikes, self.loves)
        if the_max != 0:
            size = round(100/the_max * what/6.25)
            result = ''
            if size >= 8:
                result = self.unicodebars[8] + self.unicodebars[size-8]
            else:
                result = self.unicodebars[size] + self.unicodebars[0]
        else:
            result = '  '
        return result

    def get_line(self, what):
        return '{0}{1:4d}'.format(
            self.sixteenths(what),
            what)

    @property
    def bars(self):
        result = '`😣 ' + self.get_line(self.hates) + '`\n'
        result += '`🙁 ' + self.get_line(self.dislikes) + '`\n'
        result += '`🙂 ' + self.get_line(self.likes) + '`\n'
        result += '`😊 ' + self.get_line(self.loves) + '`\n'
        return result

    @property
    def barsplus(self):
        lines = self.bars
        prefixes = ['`Hate   :` ', '`Dislike:` ', '`Like   :` ', '`Love   :` ']
        result = ''
        for idx, line in enumerate(lines.splitlines()):
            result += prefixes[idx] + line + '\n'
        return result

    @property
    def datadump(self):
        lst = [-3 for x in range(self.hates)]
        lst += [-1 for x in range(self.dislikes)]
        lst += [1 for x in range(self.likes)]
        lst += [3 for x in range(self.loves)]
        return lst

    @property
    def smiley(self):
        lst = self.datadump
        if not len(lst):
            return'-', 0
        mean = statistics.mean(lst)
        smileyindex = 0
        if mean > -1.5:
            smileyindex = 1
        if mean >= 0:
            smileyindex = 2
        if mean >= 1.5:
            smileyindex = 3
        return self.smileys[smileyindex], mean


if __name__ == "__main__":
    for items in (
        [2, 4, 6, 1],
        [1, 4, 6, 1],
        [0, 0, 0, 0],
        [1, 0, 0, 1],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ):
        print(items)
        dv = DetailVotes(*items)
        print(dv.bars)
        print(dv.smiley)
        print("#"*40)
