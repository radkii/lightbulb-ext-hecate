# Imports
from hikari import Event

# All event files declare the type of event in their name.
# Event files (and command files too) will be ignored if their name starts with _

# Necessary 'event' method that takes an hikari Event as argument.
# Prints a report every time someone deletes a message
async def event(e: Event):
    print(f"[GuildMessageDeleteEvent] {e.old_message.member.nickname or e.old_message.member.username} deleted a message")
