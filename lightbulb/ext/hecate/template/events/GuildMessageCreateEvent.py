# Imports
from hikari import Event

# All event files declare the type of event in their name

# Necessary 'event' method that takes an hikari Event as argument.
# Prints information about a message every time one is created
async def event(e: Event):
    print(f"[GuildMessageCreateEvent] {e.member.nickname or e.member.username}: {e.message.content}")
