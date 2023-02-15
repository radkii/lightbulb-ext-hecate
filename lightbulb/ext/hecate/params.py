import hikari
import lightbulb

__all__ = [
    "Option",
    "Params"
]

class Option():
    def __init__(self, name : str, description : str, var_type : hikari.OptionType) -> None:
        self.name = name
        self.description = description
        self.var_type = var_type

    def process_module(self, mod):
        mod.command = lightbulb.option(self.name, self.description, self.var_type)(mod.command)

class Params():
    def __init__(self, description : str, options=[], name="") -> None:
        self.description = description
        self.options = options
        self.name = name

    def process_module(self, mod):
        mod.command = lightbulb.command(self.name, self.description)(mod.command)
        for opt in self.options:
            opt.process_module(mod)
