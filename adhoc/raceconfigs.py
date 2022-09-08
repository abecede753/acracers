import configparser
import io


class CParser:
    def __init__(self, filename):
        self.filename = filename
        self.ini = configparser.RawConfigParser()
        self.ini.optionxform = str
        self.ini.read(filename)

    def __str__(self):
        output = io.StringIO()
        self.ini.write(output)
        output.seek(0)
        return output.read()

    def save(self):
        with open(self.filename, 'w') as outfile:
            self.ini.write(outfile, space_around_delimiters=False)


class ServerConfig(CParser):
    """AC config in cfg/server_cfg.ini in a pythonic format."""


class Driver:
    """A driver with their STEAM ID."""
    def __init__(self, name='', steam_id=''):
        self.name = name
        self.steam_id = steam_id


class Car:
    def __init__(self, model, skin, guid, fixed_setup):
        self.model = model
        self.skin = skin
        self.guid = guid
        self.fixed_setup = fixed_setup

    def __repr__(self):
        return self.model


class EntryList(CParser):
    """Driver list in cfg/entry_list.ini in a pythonic format."""

    @property
    def models(self):
        the_models = []
        for groupname in self.ini.keys():
            if 'CAR' in groupname:
                the_models.append(Car(
                    self.ini[groupname]['MODEL'],
                    self.ini[groupname]['SKIN'],
                    self.ini[groupname]['GUID'],
                    self.ini[groupname]['FIXED_SETUP']))
        return the_models
