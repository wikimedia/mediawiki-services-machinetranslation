from typing import Dict


class AbbreviationsRegistry(type):
    REGISTRY: Dict[str, type] = {}

    def __init__(cls, name, bases, attrs):
        """
        Here the name of the class is used as key but it could be any class
        parameter.
        """
        if name != "BaseAbbreviation":
            AbbreviationsRegistry.REGISTRY[cls.language] = cls

    @classmethod
    def get_registry(cls) -> Dict[str, type]:
        return cls.REGISTRY


class BaseAbbreviation(object, metaclass=AbbreviationsRegistry):
    """
    Any class that will inherits from BaseAbbrevRegisteredClass will be included
    inside the dict AbbrevRegistryHolder.REGISTRY, the key being the name of the
    class and the associated value, the class itself.
    """

    language = "base"

    def is_abbreviation(head: str, tail: str):
        raise Exception("Not implemented")
