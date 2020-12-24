import configparser
import os.path

import click


class ConfigParser:
    def __init__(self, config_name):
        self.config = {}
        if os.environ.get("FREELDEP_CONFIG", ""):
            config_name = os.environ["FREELDEP_CONFIG"]
        elif os.environ.get("FREELDEP_HOME", ""):
            config_file = self._parse_home()
            if config_file:
                config_name = config_file
        if os.path.isfile(config_name):
            self.config = configparser.ConfigParser()
            self.config.read(config_name)
        else:
            raise click.UsageError(
                "You must specify your deployment settings. Set FREELDEP_CONFIG, or FREELDEP_HOME"
                "or create a file ./config.ini"
            )

    def get(self, section, name, default=None):
        if section not in self.config.sections():
            return default
        return self.config[section].get(name, default)

    def _parse_home(self):
        folder = os.environ["FREELDEP_HOME"]
        if folder[-1] != "/":
            folder = folder + "/"
        filename = folder + "config.ini"
        if os.path.isfile(os.path.expanduser(filename)):
            return filename
