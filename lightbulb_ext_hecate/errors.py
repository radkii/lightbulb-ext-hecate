from lightbulb import LightbulbError

class HecateError(LightbulbError):
    """
    Base hecate exception class. All errors raised by hecate will be a subclass
    of this exception.
    """

class MissingParams(HecateError):
    '''
    Exception raised when a command module accessed by a hecate `Plugin` does not
    contain a `params` attribute or the required params attributes in separate.
    '''

class MissingMethod(HecateError):
    '''
    Exception raised when a module accessed by a hecate `Plugin` does not declare a
    `command` or `event` method.
    '''

class HikariEventNotFound(HecateError):
    '''
    Exception raised when an event module accessed by a hecate `Plugin` has a name
    that doesn't match any hikari events.
    '''
   