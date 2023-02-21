from .errors import PropertyBuildError

__all__ = [
    "Properties"
]

class Properties():
    '''
    Class for defining shared attributes between commands and events.

    Args:
        **kwargs (`dict`): A key-value pair related to a shared extension attribute.
        It will be resolved upon instantiating the associated extension.
    '''
    def __init__(self, **kwargs) -> None:
        self.__property_request = kwargs

    def __contains__(self, __o: object) -> bool:
        return __o in self.__property_request

    def insert(self, ext_properties: dict):
        for key in self.__property_request:
            if not key in ext_properties:
                ext_properties[key] = self.__property_request[key]
            if bool(self.__property_request[key]):
                if bool(ext_properties[key]) and ext_properties[key] != self.__property_request[key]:
                    raise PropertyBuildError(f"Conflicting assignment of truthy values to property '{key}' ({ext_properties[key]} and {self.__property_request[key]})")
                else:
                    ext_properties[key] = self.__property_request[key]

    def update(self, ext_properties: dict):
        for key in self.__property_request:
            def getter(self):
                return ext_properties[key]
            def setter(self, val):
                ext_properties[key] = val
            setattr(self.__class__, key, property(fget=getter,fset=setter))