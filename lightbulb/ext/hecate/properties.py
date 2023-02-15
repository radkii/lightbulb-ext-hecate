from .errors import PropertyBuildError

__all__ = [
    "Properties"
]

class Properties():
    def __init__(self, **kwargs) -> None:
        for key in kwargs:
            if bool(kwargs[key]):
                raise PropertyBuildError(f"Property '{key}' must be initialized with an empty value.")
        self.__property_request = kwargs

    def __contains__(self, __o: object) -> bool:
        return __o in self.__property_request

    def update(self, ext_properties: dict):
        for key in self.__property_request:
            setattr(self, key, ext_properties[key] if key in ext_properties else self.property_request[key])