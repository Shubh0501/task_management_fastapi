from enum import Enum

class LabeledStrEnum(str, Enum):
    def __new__(cls, value: str, label: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    @classmethod
    def from_label_or_value(cls, input_str: str):
        for member in cls:
            if member.value == input_str:
                return member
        for member in cls:
            if member.label == input_str:
                return member
        raise ValueError(f"{input_str} is not a valid {cls.__name__}")


class Environment(str, Enum):
    LOCAL = "LOCAL"
    STAGING = "STAGING"
    TESTING = "TESTING"
    PRODUCTION = "PRODUCTION"

    @property
    def is_debug(self):
        return self in (
            self.LOCAL,
            self.STAGING,
            self.TESTING,
        )

    @property
    def is_deployed(self) -> bool:
        return self in (self.STAGING, self.PRODUCTION)