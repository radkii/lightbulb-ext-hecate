import lightbulb
import hikari
import os
import glob
import logging
from .params import *
from .errors import *
from .properties import *
from importlib.util import spec_from_file_location

__all__ = [
    "Plugin",
    "CommandContext",
    "EventContext",
    "command_types"
]

command_types = {
    "prefix-commands": lightbulb.commands.PrefixCommand,
    "message-commands": lightbulb.commands.MessageCommand,
    "user-commands": lightbulb.commands.UserCommand,
    "slash-commands": lightbulb.commands.SlashCommand
}

_LOGGER = logging.getLogger("hecate.plugin")

class CommandContext():
    def __init__(self, category: lightbulb.commands.Command, params: Params, properties: Properties, path: str) -> None:
        self.category = category
        self.params = params
        self.properties = properties
        self.path = path

class EventContext():
    def __init__(self, category: lightbulb.commands.Command, properties: Properties, path: str) -> None:
        self.category = category
        self.properties = properties
        self.path = path

class Plugin(lightbulb.Plugin):
    def __init__(self, name: str, extension_path: str, default_properties={}, on_command_error=None,
on_event_error=None, on_command_enter=None, on_command_exit=None) -> None:
        super().__init__(name)

        self.__properties = default_properties

        modify_path = os.path.join(os.path.dirname(extension_path), '__modify__.py')
        if os.path.exists(modify_path):
            spec = spec_from_file_location('__modify__.py', modify_path)
            mod = spec.loader.load_module()
            if on_command_error == None and hasattr(mod, 'on_command_error'):
                on_command_error = mod.on_command_error
            if on_event_error == None and hasattr(mod, 'on_event_error'):
                on_event_error = mod.on_event_error
            if on_command_enter == None and hasattr(mod, 'on_command_enter'):
                on_command_enter = mod.on_command_enter
            if on_command_exit == None and hasattr(mod, 'on_command_exit'):
                on_command_exit = mod.on_command_exit

        def enter_exit_decorator(com_ctx):
            def dec(func):
                async def new_func(ctx):
                    if on_command_enter:
                        await on_command_enter(com_ctx, ctx)
                    await func(ctx)
                    if on_command_exit:
                        await on_command_exit(com_ctx, ctx)
                return new_func    
            return dec            

        # def catch_command_exceptions(func):
        #     async def new_func(ctx):
        #         try:
        #             await func(ctx)
        #         except:
        #             await on_command_error(ctx)
        #     return new_func

        # def catch_event_exceptions(func):
        #     async def new_func(e):
        #         try:
        #             await func(e)
        #         except:
        #             await on_event_error(e)
        #     return new_func

        def catch_exception_decorator(com_ctx, on_error_func):
            def dec(func):
                async def new_func(val):
                    try:
                        await func(val)
                    except:
                        await on_error_func(com_ctx, val)
                return new_func    
            return dec 


        dir_path = os.path.dirname(extension_path)
        for command in command_types:
            grab_path = os.path.join(dir_path, command)
            if not os.path.exists(grab_path):
                continue
            
            py_valid = 0
            for py_file in glob.glob(os.path.join(grab_path, "[!_]*.py")):
                py_name = os.path.basename(py_file)
                # if py_name.startswith('_'):
                #     continue

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

                com_ctx = CommandContext(
                    command_types[command], 
                    params,
                    mod.properties if hasattr(mod, 'properties') else None,
                    py_file
                )
                if on_command_enter != None or on_command_exit != None:
                    mod.command = enter_exit_decorator(com_ctx)(mod.command)
                if on_command_error != None:
                    # mod.command = catch_command_exceptions(mod.command)
                    mod.command = catch_exception_decorator(com_ctx, on_command_error)(mod.command)
                mod.command = lightbulb.implements(command_types[command])(mod.command)
                params.process_module(mod)
                mod.command = self.command()(mod.command)
                py_valid += 1
            if py_valid:
                _LOGGER.info(f"Fetched {py_valid} commands from '{command}'")
        
        event_path = os.path.join(dir_path, "events")
        if os.path.exists(event_path):
            py_valid = 0
            for py_file in glob.glob(os.path.join(event_path, "[!_]*.py")):
                py_name = os.path.basename(py_file)
                # if py_name.startswith('_'):
                #     continue

                spec = spec_from_file_location(py_name, py_file)
                mod = spec.loader.load_module()

                if not hasattr(mod, 'event'):
                    raise MissingMethodError(f"Event module '{py_name}' doesn't declare an 'event' method")

                if not hasattr(hikari, py_name[:-3]):
                    raise MissingHikariEventError(f"Event module '{py_name}' is not named after a valid event")


                e_ctx = EventContext(
                    getattr(hikari, py_name[:-3]),
                    mod.properties if hasattr(mod, 'properties') else None,
                    py_file
                )
                if on_event_error != None:
                    # mod.event = catch_event_exceptions(mod.event)
                    mod.event = catch_exception_decorator(e_ctx, on_event_error)(mod.event)
                mod.event = self.listener(getattr(hikari, py_name[:-3]))(mod.event)
                py_valid += 1
            if py_valid:
                _LOGGER.info(f"Fetched {py_valid} events")
     