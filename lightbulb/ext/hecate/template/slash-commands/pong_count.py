# Imports
from lightbulb import Context
from lightbulb.ext.hecate import Params, Properties

# Declaring command attributes with a 'Params' object.
# The 'name' attribute or Params kwarg should be set if the command
# is to have a different name from the file name
params = Params(
    description="Returns the number of pongs delivered",
    name='count'
)

# Declaring a 'pongs' shared attribute so the two commands work together
properties = Properties(pongs=0)

# Necessary 'command' method, that takes a Context object as argument.
# Responds with the number of pongs
async def command(ctx: Context):
    await ctx.respond(f"{properties.pongs} pongs to date")