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
    def __init__(self, name='', steam_id='', car=None):
        self.name = name
        self.steam_id = steam_id
        self.car = car

    def __repr__(self):
        return self.name


class Car:
    """available car for the event."""
    def __init__(self, carindex, model, skin, fixed_setup):
        self.carindex = carindex  # 0=fastest, 1=a bit slower, ...
        self.model = model
        self.skin = skin
        self.fixed_setup = fixed_setup

    def __repr__(self):
        return self.model


class EntryList(CParser):
    """Driver list in cfg/entry_list.ini in a pythonic format."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.distinct_cars = self._get_cars()

    def _get_cars(self):
        """get the different car models. (equals number of rounds)"""
        the_cars = []
        carindex = 0
        for groupname in self.ini.keys():
            if 'CAR' in groupname:
                the_cars.append(Car(
                    carindex,
                    self.ini[groupname].get('MODEL'),
                    self.ini[groupname].get('SKIN'),
                    self.ini[groupname].get('FIXED_SETUP'),
                    ))
                carindex += 1
        return the_cars


class ServerSetup:
    """the complete server setup."""

    def __init__(self, server_cfg_filename, entry_list_filename):
        self.server_cfg = ServerConfig(server_cfg_filename)
        self.entry_list = EntryList(entry_list_filename)

        self.drivers = []
        
        # self.server.serverconfig.ini['SERVER']['CARS'] = self.cars[0]

    @property
    def rounds(self):
        return len(self.entry_list.distinct_cars)

    def write(self, race_number):
        """overwrite server_cfg.ini and entry_list.ini
        according to current values."""




