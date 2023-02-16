# Imports
from lightbulb import Context
from lightbulb.ext.hecate import Params, Properties

# Declaring command attributes with a 'Params' object
params = Params(
    description="Returns the number of pongs delivered",
    name='count'
)

# Declaring a 'pongs' shared attribute so the two commands work together
properties = Properties(pongs=0)

# Necessary 'command' method, that takes a Context object as argument
def command(ctx: Context):
    ctx.respond(f"{properties.pongs} pongs to date")