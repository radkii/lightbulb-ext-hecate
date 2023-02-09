import hikari
import lightbulb

class Option():
    def __init__(self, name : str, description : str, var_type : hikari.OptionType) -> None:
        self.__name = name
        self.__description = description
        self.__var_type = var_type

    def process_module(self, mod):
        mod.command = lightbulb.option(self.__name, self.__description, self.__var_type)(mod.command)

class Params():
    def __init__(self, description : str, options=[], name="") -> None:
        self.__description = description
        self.__options = options
        self.__name = name

    def process_module(self, mod):
        mod.command = lightbulb.command(self.__name, self.__description)(mod.command)
        for opt in self.__options:
            opt.process_module(mod)