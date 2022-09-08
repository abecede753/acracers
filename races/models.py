import configparser
import datetime
import glob
import json
import os
import shutil
import tarfile
import tempfile

from django.conf import settings
from django.db import models

from races import defaults as _D
from easy_thumbnails.fields import ThumbnailerImageField


def set_start_timestamp(delay_minutes=2):
    return datetime.datetime.now() + datetime.timedelta(delay_minutes)


class RaceQueue(models.Model):
    setup = models.ForeignKey('races.RaceSetup', on_delete=models.CASCADE)
    index = models.IntegerField()
    options = models.TextField(default='')

    def __str__(self):
        return str(self.setup)


def cleanup_RaceQueue_indices():
    current_index = 1
    for rq in RaceQueue.objects.all().order_by('index'):
        rq.index = current_index
        rq.save()
        current_index += 1


class RaceSetup(models.Model):
    """we call this "combo" for our users"""
    title = models.CharField(max_length=32, unique=True)
    description = models.TextField(default="no description")
    tgz = models.FileField(upload_to='tgz/', null=True, blank=True)
    image = ThumbnailerImageField(null=True, upload_to='images/')
    car_download_url = models.URLField(max_length=2048, blank=True, default='')
    track_download_url = models.URLField(max_length=2048, blank=True,
                                         default='')
    car_override = models.BooleanField(default=False)
    track_override = models.BooleanField(default=False)
    fixed_cars = models.BooleanField(default=False)
    randomizable = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    hidden = models.BooleanField(default=False)
    imgurlink = models.URLField(max_length=2048, blank=True, default='')
    tierdrop = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def unpack_for_acserver(self, targetdir=None):
        """returns the cfg directory"""
        sessionrootdir = targetdir or settings.ACSERVERROOT
        tar = tarfile.open(self.tgz.file.name)
        shutil.rmtree(sessionrootdir)
        shutil.copytree(settings.ACSERVERWRAPPERROOT, sessionrootdir,
                        symlinks=True, dirs_exist_ok=False)
        shutil.copy(settings.ACSERVEREXE, sessionrootdir)
        tar.extractall(path=sessionrootdir)
        os.mkdir(os.path.join(sessionrootdir, 'results'))
        return os.path.join(sessionrootdir, 'cfg')

    # def set_cm_text(self, directory):
    #     """based on "directory" makes a nice description
    #     including image tag for CM"""
    #     with open(os.path.join(directory, 'cfg',
    #                            'cm_wrapper_params.json')) as jsonfile:
    #         content = json.load(jsonfile)
    #     with open(os.path.join(directory, 'cfg',
    #                            'cm_wrapper_params.json'), 'w') as jsonfile:
    #         content = json.dump(content, jsonfile)

    def get_car_track_urls_from_cfg(self, directory):
        """XXX: only works for ONE car model. not multiple car models."""
        with open(os.path.join(directory, 'cfg', 'cm_content',
                               'content.json')) as jsonfile:
            content = json.load(jsonfile)

        result = {'car': None, 'track': None}
        try:
            carname = list(content['cars'].keys())[0]
            result['car'] = content['cars'][carname]['url']
        except Exception:
            pass
        try:
            result['track'] = content['track']['url']
        except Exception:
            pass
        return result

    def fix_cm_wrapper_params(self, directory):
        """ensures the we have the correct wrapper port,
        description etc.
        just create a "standard" config
        also take care of car / track overrides.
        returns `True` if model has changed."""
        dirty = False
        with open(os.path.join(directory, 'cfg',
                               'cm_wrapper_params.json')) as jsonfile:
            content = json.load(jsonfile)
        content['port'] = _D.ACSERVERWRAPPERPORT
        content['downloadPasswordOnly'] = False
        urls = self.get_car_track_urls_from_cfg(directory)
        if self.car_override and self.car_download_url:
            urls['car'] = self.car_download_url
        if self.track_override and self.track_download_url:
            urls['track'] = self.track_download_url

        downloadtext = '\n'
        if urls.get('car'):
            downloadtext += '[url={0}]download car[/url]  '.format(urls['car'])
            if not self.car_override:
                if self.car_download_url != urls['car']:
                    self.car_download_url = urls['car']
                    dirty = True
        if urls.get('track'):
            downloadtext += '[url={0}]download track[/url]\n'.format(
                urls['track'])
            if not self.track_override:
                if self.track_download_url != urls['track']:
                    self.track_download_url = urls['track']
                    dirty = True

        content['description'] = _D.BASE_DESCRIPTION.format(
            title=self.title,
            image=self.image.url,
            description=self.description,
            downloadtext=downloadtext
        )
        # import pdb; pdb.set_trace()
        with open(os.path.join(directory, 'cfg',
                               'cm_wrapper_params.json'), 'w') as jsonfile:
            content = json.dump(content, jsonfile)
        return dirty

    def fix_server_cfg(self, directory):
        """ensures the we have the correct admin password,
        wrapper port etc."""
        config = configparser.ConfigParser()
        config.optionxform = lambda option: option  # keep uppercase keys
        filename = os.path.join(directory, 'cfg', 'server_cfg.ini')
        config.read(filename)
        config["SERVER"]["NAME"] = _D.RACENAME.format(self.title)
        config["SERVER"]["ADMIN_PASSWORD"] = _D.ADMIN_PASSWORD
        config["SERVER"]["LOOP_MODE"] = "0"
        config["SERVER"]["WELCOME_MESSAGE"] = "welcome.txt"

        try:  # combo may not have a race
            config["RACE"]["IS_OPEN"] = "1"
        except Exception:
            pass

        try:  # combo may not have a qualify round...
            config["QUALIFY"]["IS_OPEN"] = "1"
        except Exception:
            pass

        # conversion from qualify to practice - we won't do qualifying anymore
        if 'QUALIFY' in config.sections() and \
           '__CM_PRACTICE_OFF' in config.sections():
            items = config.items('QUALIFY')
            config.add_section('PRACTICE')
            for item in items:
                config.set('PRACTICE', item[0], item[1])
            config.remove_section('QUALIFY')
            config.remove_section('__CM_PRACTICE_OFF')

        # conversion from 2 races to just 1 race
        config['SERVER']['REVERSED_GRID_RACE_POSITIONS'] = '0'

        # reduce damage multiplier to at most 50
        try:
            dm = int(config['SERVER']['DAMAGE_MULTIPLIER'])
            if dm > 50:
                config['SERVER']['DAMAGE_MULTIPLIER'] = '50'
        except Exception:
            pass

        # wait time before race should be exactly 20 seconds
        try:
            wt = int(config['RACE']['WAIT_TIME'])
            if wt != 20:
                config['RACE']['WAIT_TIME'] = '20'
        except Exception:
            pass
        with open(filename, 'w') as configfile:
            config.write(configfile, space_around_delimiters=False)

    def fix_entry_list(self, directory):
        """ensures the we have fixed setups (if there's a setup file here)"""
        cfgdir = os.path.join(directory, 'cfg')
        fnames = [os.path.basename(x) for x in
                  glob.glob('{0}/*.ini'.format(cfgdir))]
        for ignore in ("entry_list.ini", "server_cfg.ini"):
            try:
                fnames.remove(ignore)
            except ValueError:
                pass
        if len(fnames) != 1:  # there isn't exactly one file left
            return

        fixedsetupfilename = fnames[0]

        config = configparser.ConfigParser()
        config.optionxform = lambda option: option
        filename = os.path.join(cfgdir, 'entry_list.ini')
        config.read(filename)
        for carname in config:
            if carname.startswith("CAR_"):
                config[carname]['FIXED_SETUP'] = fixedsetupfilename
        with open(filename, 'w') as configfile:
            config.write(configfile, space_around_delimiters=False)

        # make "setups" directory for the fixed setup file
        # and put the fixedsetupfile into it.
        os.makedirs(os.path.join(directory, "setups"), exist_ok=True)
        os.rename(os.path.join(directory, 'cfg', fixedsetupfilename),
                  os.path.join(directory, 'setups', fixedsetupfilename))

    def _cleanup(self):
        """make sure that our settings like adminpassword, description,
        port etc. are okay"""
        dirty = False
        with tempfile.TemporaryDirectory() as tmpdirname:
            with tarfile.open(self.tgz.file.name) as tar:
                tar.extractall(path=tmpdirname)

            dirty = dirty or self.fix_cm_wrapper_params(tmpdirname)
            self.fix_server_cfg(tmpdirname)
            if not self.fixed_cars:
                self.fix_entry_list(tmpdirname)

            os.unlink(self.tgz.file.name)
            with tarfile.open(name=self.tgz.file.name, mode='x:gz') as tar:
                for name in os.listdir(tmpdirname):
                    tar.add(os.path.join(tmpdirname, name), arcname=name)
        return dirty

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._cleanup():
            super().save(*args, **kwargs)  # model has changed. must save again


# class Race(models.Model):
#     start_ts = models.DateTimeField(auto_now_add=True)
#     racesetup = models.ForeignKey(RaceSetup,
#                                   on_delete=models.CASCADE)
#     stdout = models.TextField(default='')
#     stderr = models.TextField(default='')
# 
#     end_ts = models.DateTimeField(null=True)
# 
#     def __str__(self):
#         return self.racesetup.title
# 
# 
# class Poll(models.Model):
#     racesetups = models.ManyToManyField(RaceSetup, through='Voting')
#     js = models.TextField(default='', null=True, blank=True)
# 
# 
# class Voting(models.Model):
#     racesetup = models.ForeignKey(RaceSetup, on_delete=models.CASCADE)
#     poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
#     points = models.IntegerField(default=0)
# 
# 
# class Vote(models.Model):
#     discorduser = models.CharField(max_length=1024)
#     racesetup = models.ForeignKey(RaceSetup, on_delete=models.CASCADE)
#     value = models.SmallIntegerField()
