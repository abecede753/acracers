import argparse
import configparser
import os

from django.conf import settings


class ContinuingParser(argparse.ArgumentParser):

    def error(self, message):
        raise Exception


def parse_options(something=''):
    if isinstance(something, str):
        something = something.split()
    parser = ContinuingParser()
    parser.add_argument('-p', type=int)
    parser.add_argument('-r', type=int)
    parser.add_argument('-o', action='store_true')
    cfg = parser.parse_args(something)
    return cfg


def set_live_options(something=''):
    cfg = parse_options(something)
    if cfg.p and cfg.p > 0 and cfg.p < 61:
        update_server_cfg_file('PRACTICE', 'TIME', str(cfg.p))
    if cfg.r and cfg.r > 0 and cfg.r < 61:
        update_server_cfg_file('RACE', 'TIME', str(cfg.r))
    if cfg.o:
        remove_fixed_setup()
    return cfg


def update_server_cfg_file(group, item, value):
    filename = os.path.join(settings.ACSERVERROOT, 'cfg', 'server_cfg.ini')
    config = configparser.ConfigParser()
    config.optionxform = lambda option: option  # keep uppercase keys
    config.read(filename)
    config[group][item] = str(value)
    with open(filename, 'w') as configfile:
        config.write(configfile, space_around_delimiters=False)


def remove_fixed_setup():
    filename = os.path.join(settings.ACSERVERROOT, 'cfg', 'entry_list.ini')
    with open(filename, 'r') as f:
        content = f.read()
    with open(filename, 'w') as f:
        for line in content.splitlines(keepends=True):
            if line.startswith('FIXED_SETUP='):
                continue
            f.write(line)
    return
