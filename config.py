import configparser
import os


class EnvInterpolation(configparser.ExtendedInterpolation):

    def before_read(self, parser, section, option, value):
        value = super().before_read(parser, section, option, value)
        os_value = os.getenv(option.upper())
        return os_value if os_value else value


# Initiate config parser
config = configparser.ConfigParser(interpolation=EnvInterpolation())
config.read("config.ini")
