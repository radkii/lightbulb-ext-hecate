# Imports
from lightbulb import Context
from lightbulb.ext.hecate import Option, Properties

# Declaring a 'description' attribute sets the description of the command.
# Equivalent to:
# params = Params(description="...", ...)
description = "Replies with 'Pong!'"

# Declaring an 'options' attribute sets the options of the command.
# Equivalent to:
# params = Params(options=[...], ...)
options = [
    Option('amount', "Number of times to ping", int)
]

# Declaring a 'pongs' shared attribute so the two commands work together
properties = Properties(pongs=0)

# Necessary 'command' method, that takes a Context object as argument.
# Increments the number of pongs by the 'amount' option, and raises ValueError
# if it's less than 1 
async def command(ctx: Context):
    cur_pongs = ctx.options.amount
    if cur_pongs < 1:
        raise ValueError
    properties.pongs += cur_pongs
    await ctx.respond(f"Pong! x{cur_pongs}" if cur_pongs > 1 else "Pong!")