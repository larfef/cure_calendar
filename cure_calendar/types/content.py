from enum import IntEnum
from typing import TypedDict


class TextType(IntEnum):
    DEFAULT = 0
    PRODUCT_LABEL = 1
    RESTART_PRODUCT = 2
    STOP_PRODUCT = 3
    PAUSE = 4
    FINISH_PRODUCT = 5


class ContentType(IntEnum):
    CELL = 0
    GREEN_LINE = 1
    RED_LINE = 2
    ARROW = 3
    PAUSE = 4


class TextDict(TypedDict):
    value: str
    type: TextType
    enabled: bool


class SegmentContent(TypedDict):
    end: int
    product: dict | None
    start: int
    text: TextDict | None
    type: str
