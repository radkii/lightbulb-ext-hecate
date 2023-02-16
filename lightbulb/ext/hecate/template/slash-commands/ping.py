from lightbulb import Context

description = "Replies with 'Pong!'"

def command(ctx: Context):
    ctx.respond("Pong!")