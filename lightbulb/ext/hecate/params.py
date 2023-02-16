import hikari
import lightbulb

__all__ = [
    "Option",
    "Params"
]

class Option():
    '''
    Class that serves as an option for a given command. Should always be instantiated
    as an element of an `options` attribute or passed into a `Params` class.

    Args:
        name (`str`): The name of the option, often in python_case.
        description (`str`): The description of the option.
        var_type (`hikari.OptionType`): The type of variable the option takes.
    '''
    def __init__(
        self, 
        name: str, 
        description: str, 
        var_type: hikari.OptionType
    ) -> None:
        self.name = name
        self.description = description
        self.var_type = var_type

    def process_module(self, mod):
        mod.command = lightbulb.option(self.name, self.description, self.var_type)(mod.command)

class Params():
    '''
    Class that serves as the parameters for a given command. Should always be assigned to a 
    `params` attribute in the command file. All the argument names of the `Params` class
    constructor can also be used to define attributes, which will achieve the same effect.

    Args:
        description (`str`): The description of the command.
        options (`list[hecate.Option]`): All the options of the command. `[]` by default.
        name (`str`): The name of the command. `""` by default, which grabs the name from
        the file.
    '''
    def __init__(self, description: str, options=[], name="") -> None:
        self.description = description
        self.options = options
        self.name = name

    def process_module(self, mod):
        mod.command = lightbulb.command(self.name, self.description)(mod.command)
        for opt in self.options:
            opt.process_module(mod)
