from typing import List, Dict
from enum import StrEnum as _StrEnum


class ElementalStrEnum(_StrEnum):
    """
    A base class for string-based enumerations.

    Ideal for scenarios where enumeration members map directly to string values, such as
    constants for keys, labels, or descriptive values. This class inherits from Python's
    `Enum`, enabling full enumeration functionality while strictly supporting string values.

    Example:
        ```
        class Color(StrEnum):
            RED = "red"
            GREEN = "green"
            BLUE = "blue"
        ```

    Attributes:
        - Enum members are expected to have string values.
    """

    @classmethod
    def to_list(cls) -> List[str]:
        return [member for member in cls]

    @classmethod
    def to_dict(cls) -> Dict[str, str]:
        return {member.name: member for member in cls}
