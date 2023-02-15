from .errors import PropertyBuildError

__all__ = [
    "Properties"
]

class Properties(dict):
    def __init__(self, **kwargs) -> None:
        for key in kwargs:
            if bool(kwargs[key]):
                raise PropertyBuildError(f"Property '{key}' must be initialized with an empty value.")
        self.property_request = kwargs

    def update(self, ext_properties: dict):
        for key in self.property_request:
            setattr(self, key, ext_properties[key] if key in ext_properties else self.property_request[key])