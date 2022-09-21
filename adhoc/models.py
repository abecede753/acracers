import json
import os
import pathlib

from django.conf import settings
from django.db import models
from django.template.loader import get_template
from django.utils import timezone

from adhoc.raceconfigs import ServerConfig, EntryList
from main.acserver import ac_run
from races.models import RaceSetup
from races.tierdrop import Tierdrop


def cleanup_AdhocRace_indices():
    current_index = 1
    allars = list(
        AdhocRace.objects.filter(
            index__isnull=False, start_ts__isnull=True).order_by('index')
    ) + list(AdhocRace.objects.filter(
        index__isnull=True, start_ts__isnull=True).order_by('pk'))

    for rq in allars:
        rq.index = current_index
        rq.save()
        current_index += 1


class AdhocRace(models.Model):
    START_RULES = [(0, 'cars locked until start'),
                   (1, 'teleport false starters to pits'),
                   (2, 'false starters must do a pit drivethru')]
    index = models.IntegerField(null=True)
    racesetup = models.ForeignKey(RaceSetup,
                                  on_delete=models.CASCADE)
    start_ts = models.DateTimeField(null=True, default=None, blank=True)
    end_ts = models.DateTimeField(null=True, default=None, blank=True)
    stderr = models.TextField(default='', blank=True)
    stdout = models.TextField(default='', blank=True)
    result = models.TextField(default='', null=True, blank=True)
    practice_minutes = models.IntegerField(default=0)
    qualifying_minutes = models.IntegerField(default=10)
    race_minutes = models.IntegerField(default=15)
    reverse_grid = models.IntegerField(default=0)
    join_password = models.CharField(max_length=15, default='', blank=True,
                                     null=False)
    admin_password = models.CharField(
        max_length=15, default=settings.DEFAULT_ADMIN_PASSWORD)
    fixed_setups = models.BooleanField(default=False)
    show_public = models.BooleanField(default=False)
    start_rule = models.IntegerField(default=0, choices=START_RULES)
    run_forever = models.BooleanField(default=False)

    finished = False  # for adhocserver, especially dierdrop races

    def __str__(self):
        return "{0}".format(self.racesetup.title)

    def startup(self, overrides):
        """overrides is a dictionary containing server setting stuff like
        ```
        {'SERVER': {'HTTP_PORT':8081, 'UDP_PORT': 9600,
                    'NAME': 'my cool server'},
         'WEATHER_0': {'GRAPHICS':'3_clear'}
        }``
        """
        self.sessioncfgdir = self.racesetup.unpack_for_acserver()
        self.sessiondir = (pathlib.Path(self.sessioncfgdir) / '..').resolve()

        # alter ini files...
        self.serverconfig = ServerConfig(
            os.path.join(self.sessioncfgdir, 'server_cfg.ini'))
        self.entrylist = EntryList(
            os.path.join(self.sessioncfgdir, 'entry_list.ini'))

        srv = self.serverconfig.ini
        for sectionname in 'PRACTICE RACE QUALIFY'.split():
            try:
                srv.remove_section(sectionname)
            except Exception:
                pass

        # TODO acserverwrapper json port festlegen!
        #         ACSERVERWRAPPERPORT = 8991
        #         RACENAME = '{0}ℹ{1}'.format('{0}', ACSERVERWRAPPERPORT)
        #         BASE_DESCRIPTION = """[img=https://acr
        # acers.com/{image}]{title}[/img]
        # {description}
        # {downloadtext}"""
        #         srv['SERVER']

        if self.practice_minutes > 0:
            srv['PRACTICE'] = {}
            srv['PRACTICE']['TIME'] = str(self.practice_minutes)
            srv['PRACTICE']['NAME'] = 'Practice'
            srv['PRACTICE']['IS_OPEN'] = '1'
        if self.qualifying_minutes > 0:
            srv['QUALIFY'] = {}
            srv['QUALIFY']['TIME'] = str(self.qualifying_minutes)
            srv['QUALIFY']['NAME'] = 'Qualify'
            srv['QUALIFY']['IS_OPEN'] = '1'
        if self.race_minutes > 0:
            srv['RACE'] = {}
            srv['RACE']['TIME'] = str(self.race_minutes)
            srv['RACE']['WAIT_TIME'] = '30'
            srv['RACE']['NAME'] = 'Race'
            srv['RACE']['IS_OPEN'] = '2'
            if self.reverse_grid:
                srv['SERVER']['REVERSED_GRID_RACE_POSITIONS'] = \
                        str(self.reverse_grid)
        srv['SERVER']['REGISTER_TO_LOBBY'] = '1' if self.show_public else '0'
        srv['SERVER']['ADMIN_PASSWORD'] = self.admin_password
        if self.join_password:
            srv['SERVER']['PASSWORD'] = self.join_password
        srv['SERVER']['START_RULE'] = str(self.start_rule)
        srv['SERVER']['LOOP_MODE'] = "1" if self.run_forever else "0"

        # TODO make this modifiable
        srv['SERVER']['AUTOCLUTCH_ALLOWED'] = '1'
        srv['SERVER']['STABILITY_ALLOWED'] = '1'
        srv['SERVER']['ABS_ALLOWED'] = '1'
        srv['SERVER']['TC_ALLOWED'] = '1'

        if not self.fixed_setups:
            entries = self.entrylist.ini
            for section in entries.sections():
                try:
                    del entries[section]['FIXED_SETUP']
                except Exception:
                    pass

        # tcp udp ports etc.
        if overrides:
            for section in overrides.keys():
                for key, value in overrides[section].items():
                    if not srv.has_section(section):
                        srv[section] = {}
                    srv[section][key] = str(value)

        self.serverconfig.save()
        self.entrylist.save()
        self.fix_download_urls()

        # welcome txt
        tmpl = get_template('main/welcomes/onerace.txt')
        if self.run_forever:
            tmpl = get_template('main/welcomes/loop.txt')
        (self.sessiondir / 'welcome.txt').write_text(tmpl.render())

        self.start_ts = timezone.now()
        self.index = None  # remove this adhocrace from queue
        self.save()
        cleanup_AdhocRace_indices()

    def fix_download_urls(self):
        """make sure the download urls are correct, if we have
        car/track overrides in the racesetup model."""
        dirty = False
        wrapperjson = os.path.join(self.sessioncfgdir,
                                   'cm_content/content.json')
        with open(wrapperjson) as jsonfile:
            content = json.load(jsonfile)

        if self.racesetup.car_override:
            try:
                carid = list(content['cars'].keys())[0]
                content['cars'][carid]['url'] = self.racesetup.car_download_url
                dirty = True
            except Exception:
                pass
        if self.racesetup.track_override:
            try:
                content['track']['url'] = self.racesetup.track_download_url
                dirty = True
            except Exception:
                pass
        if dirty:
            with open(wrapperjson, 'w') as jsonfile:
                json.dump(content, jsonfile)

    def run(self):
        if self.racesetup.tierdrop:
            Tierdrop(self).run()
        else:
            ac_run()

    @property
    def result_available(self):
        return self.teardown(delete=False)

    def teardown(self, delete=True):
        have_result = False
        resultsdir = self.sessiondir / "results"
        self.result = ''
        if resultsdir.is_dir():
            for child in resultsdir.iterdir():
                if 'RACE' in child.as_posix():
                    have_result = True
                    self.result += child.read_text() + '\n'
        self.end_ts = timezone.now()
        self.save()
        return have_result
