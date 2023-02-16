from lightbulb.ext.hecate import CommandContext, EventContext
from lightbulb import Context
import hikari

# Handles event errors
async def on_event_error(e_ctx: EventContext, e: hikari.Event):
    pass

# Handles command errors
async def on_command_error(com_ctx: CommandContext, ctx: Context):
    pass

# Called before a command is ran
async def on_command_enter(com_ctx: CommandContext, ctx: Context):
    pass

# Called after a command is ran
async def on_command_exit(com_ctx: CommandContext, ctx: Context):
    pass