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

def hastypedattr(obj, name, type):
    return hasattr(obj, name) and isinstance(getattr(obj, name), type)

class CommandContext():
    '''
    Class that holds information about a given command.

    Args:
        category (`lightbulb.commands.Command`): The `Command` subclass that the given command
        is associated to.
        params (`hecate.Params`): The params object found in the command file.
        properties (`hecate.Properties`): The properties object found in the command file.
        path (`str`): The path of the command file.
    '''
    def __init__(self, category: lightbulb.commands.Command, params: Params, properties: Properties, path: str) -> None:
        self.category = category
        self.params = params
        self.properties = properties
        self.path = path

class EventContext():
    '''
    Class that holds information about a given event.

    Args:
        category (`hikari.Event`): The `Event` subclass that the given event
        is associated to.
        properties (`hecate.Properties`): The properties object found in the event file.
        path (`str`): The path of the event file.
    '''
    def __init__(self, category: hikari.Event, properties: Properties, path: str) -> None:
        self.category = category
        self.properties = properties
        self.path = path

class Plugin(lightbulb.Plugin):
    '''
    Subclass of `lightbulb.Plugin` that grabs all commands and events in specific directories,
    on instantiation.

    Args:
        name (`str`): Name of the plugin.
        extension_path (`str`): Path to the extension, which will always be `__file__`.
        default_properties (`dict`): Mapping with the default value that should be given to
        all `Properties` objects that request it.
        on_command_error (`method`): Error handling method for commands. If passed here,
        overwrites the one defined in `__modify__.py`. `None` by default.
        on_event_error (`method`): Error handling method for events. If passed here,
        overwrites the one defined in `__modify__.py`. `None` by default.
        on_command_enter(`method`): Called before every command. If passed here,
        overwrites the one defined in `__modify__.py`. `None` by default.
        on_command_exit (`method`): Called after every command. If passed here,
        overwrites the one defined in `__modify__.py`. `None` by default.
    '''
    def __init__(
        self, 
        name: str, 
        extension_path: str, 
        default_properties={}, 
        on_command_error=None,
        on_event_error=None, 
        on_command_enter=None, 
        on_command_exit=None, 
        description=None,
        include_datastore=False,
        default_enabled_guilds=hikari.UNDEFINED
    ) -> None:
        super().__init__(name, description, include_datastore, default_enabled_guilds)

        self.__properties = default_properties
        #self.__extension_path = extension_path
        self.__dir_path = os.path.dirname(extension_path)

        modify_path = os.path.join(self.__dir_path, '__modify__.py')
        if os.path.exists(modify_path):
            mod = spec_from_file_location('__modify__.py', modify_path).loader.load_module()
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

        def catch_exception_decorator(com_ctx, on_error_func):
            def dec(func):
                async def new_func(val):
                    try:
                        await func(val)
                    except:
                        await on_error_func(com_ctx, val)
                return new_func    
            return dec 

        property_mods = []
        for command in command_types:
            # grab_path = os.path.join(self.__dir_path, command)
            # if not os.path.exists(grab_path):
            #     continue
            
            py_valid = 0
            for py_file in self.__call__(command):
                py_name = os.path.basename(py_file)

                mod = spec_from_file_location(py_name, py_file).loader.load_module()

                if not hasattr(mod, 'command'):
                    raise MissingMethodError(f"Command module '{py_name}' doesn't declare a 'command' method")

                has_properties = hastypedattr(mod, 'properties', Properties)
                if has_properties:
                    # mod.properties.update(self.__properties)
                    property_mods.append(mod)

                params = None
                if hasattr(mod, 'params') and isinstance(mod.params, Params):
                    params = mod.params
                elif hasattr(mod, 'description') and isinstance(mod.description, str):
                    params = Params(
                        description=mod.description,
                        options=mod.options if hastypedattr(mod, 'options', list) else [],
                        name=mod.name if hastypedattr(mod, 'name', str) else py_name[:-3],
                    )
                else:
                    raise MissingParamsError(f"Command module '{py_name}' doesn't contain the necessary attributes")

                com_ctx = CommandContext(
                    command_types[command], 
                    params,
                    mod.properties if has_properties else None,
                    py_file
                )
                if on_command_enter != None or on_command_exit != None:
                    mod.command = enter_exit_decorator(com_ctx)(mod.command)
                if on_command_error != None:
                    mod.command = catch_exception_decorator(com_ctx, on_command_error)(mod.command)
                mod.command = lightbulb.implements(command_types[command])(mod.command)
                params.process_module(mod)
                mod.command = self.command()(mod.command)
                py_valid += 1
            if py_valid:
                _LOGGER.info(f"Fetched {py_valid} commands from '{command}'")
        
        # for command in command_types:
        #     for py_file in self.__call__(command):
        #         py_name = os.path.basename(py_file)
        #         mod = spec_from_file_location(py_name, py_file).loader.load_module()
        #         if hasattr(mod, 'properties') and isinstance(mod.properties, Properties):
        #             property_mods.append(mod)
        
        for mod in property_mods:
            mod.properties.insert(self.__properties)
        for mod in property_mods:
            mod.properties.update(self.__properties)

        py_valid = 0
        for py_file in self.__call__('events'):
            py_name = os.path.basename(py_file)

            mod = spec_from_file_location(py_name, py_file).loader.load_module()

            if not hasattr(mod, 'event'):
                raise MissingMethodError(f"Event module '{py_name}' doesn't declare an 'event' method")

            if not hasattr(hikari, py_name[:-3]):
                raise MissingHikariEventError(f"Event module '{py_name}' is not named after a valid event")

            e_ctx = EventContext(
                getattr(hikari, py_name[:-3]),
                mod.properties if hastypedattr(mod, 'properties', Properties) else None,
                py_file
            )
            if on_event_error != None:
                mod.event = catch_exception_decorator(e_ctx, on_event_error)(mod.event)
            mod.event = self.listener(getattr(hikari, py_name[:-3]))(mod.event)
            py_valid += 1
        if py_valid:
            _LOGGER.info(f"Fetched {py_valid} events")

    def __call__(self, type_str: str):
        if not type_str in command_types and type_str != 'events':
            raise ValueError
        new_path = os.path.join(self.__dir_path, type_str)
        if not os.path.exists(new_path):
            return iter([])
        return iter(glob.glob(os.path.join(self.__dir_path, type_str, "[!_]*.py")))