import lightbulb
import hikari
import os
import glob
import logging
from .params import *
from .errors import *
from .props import *
from importlib.util import spec_from_file_location

__all__ = [
    "Plugin"
]

_LOGGER = logging.getLogger("hecate.plugin")

class Plugin(lightbulb.Plugin):
    def __init__(self, name: str, extension_path: str, default_properties={}, on_command_error=None, on_event_error=None) -> None:
        super().__init__(name)

        self.__command_types = {
            "prefix-commands": lightbulb.commands.PrefixCommand,
            "message-commands": lightbulb.commands.MessageCommand,
            "user-commands": lightbulb.commands.UserCommand,
            "slash-commands": lightbulb.commands.SlashCommand
        }

        self.__properties = default_properties

        def catch_command_exceptions(func):
            async def new_func(ctx):
                try:
                    await func(ctx)
                except:
                    await on_command_error(ctx)
            return new_func

        def catch_event_exceptions(func):
            async def new_func(e):
                try:
                    await func(e)
                except:
                    await on_event_error(e)
            return new_func

        dir_path = os.path.dirname(extension_path)
        for command in self.__command_types:
            grab_path = os.path.join(dir_path, command)
            if not os.path.exists(grab_path):
                continue
            
            py_valid = 0
            for py_file in glob.glob(os.path.join(grab_path, "*.py")):
                py_name = os.path.basename(py_file)
                if py_name.startswith('_'):
                    continue

                spec = spec_from_file_location(py_name, py_file)
                mod = spec.loader.load_module()

                if not hasattr(mod, 'command'):
                    raise MissingMethodError(f"Command module '{py_name}' doesn't declare a 'command' method")

                if hasattr(mod, 'properties') and isinstance(mod.properties, Properties):
                    mod.properties.update(self.__properties)

                params = None
                if hasattr(mod, 'params') and isinstance(mod.params, Params):
                    params = mod.params
                elif hasattr(mod, 'description') and isinstance(mod.description, str):
                    params = Params(
                        description=mod.description,
                        options=mod.options if hasattr(mod, 'options') else [],
                        name=mod.name if hasattr(mod, 'name') else py_name[:-3],
                    )
                else:
                    raise MissingParamsError(f"Command module '{py_name}' doesn't contain the necessary attributes")

                if on_command_error != None:
                    mod.command = catch_command_exceptions(mod.command)
                mod.command = lightbulb.implements(self.__command_types[command])(mod.command)
                params.process_module(mod)
                mod.command = self.command()(mod.command)
                py_valid += 1
            if py_valid:
                _LOGGER.info(f"Fetched {py_valid} commands from '{command}'")
        
        event_path = os.path.join(dir_path, "events")
        if os.path.exists(event_path):
            py_valid = 0
            for py_file in glob.glob(os.path.join(event_path, "*.py")):
                py_name = os.path.basename(py_file)
                if py_name.startswith('_'):
                    continue

                spec = spec_from_file_location(py_name, py_file)
                mod = spec.loader.load_module()

                if not hasattr(mod, 'event'):
                    raise MissingMethodError(f"Event module '{py_name}' doesn't declare an 'event' method")

                if not hasattr(hikari, py_name[:-3]):
                    raise MissingHikariEventError(f"Event module '{py_name}' is not named after a valid event")

                if on_event_error != None:
                    mod.event = catch_event_exceptions(mod.event)
                mod.event = self.listener(getattr(hikari, py_name[:-3]))(mod.event)
                py_valid += 1
            if py_valid:
                _LOGGER.info(f"Fetched {py_valid} events")
     