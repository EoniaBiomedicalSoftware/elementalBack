from typing import List, Dict
from typing import Union
from enum import Enum
from enum import IntEnum as _IntEnum


class ElementalIntEnum(_IntEnum, Enum):
    """
    A base class for integer-based enumerations.

    This class combines Python's `IntEnum` and `Enum` to allow enum members to be integers
    while still providing full enumeration functionality. Useful for scenarios like
    database keys, numeric states, or API status codes.

    Example:
        ```
        class Status(NumEnum):
            ACTIVE = 1
            INACTIVE = 0
            PENDING = 2
        ```

    Attributes:
        - Enum members are expected to have integer values.
        - Can be directly used in comparisons or as numeric values.
    """
    @classmethod
    def to_list(cls) -> List[Union[float, int]]:
        return [member.value for member in cls]

    @classmethod
    def to_dict(cls) -> Dict[str, Union[float, int]]:
        return {member.name: member for member in cls}