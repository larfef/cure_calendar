from dataclasses import dataclass
from typing import Callable
from cure_calendar.services.rules.specs import ContentSpec


@dataclass
class Rule:
    """A rule for determining what content to add to a week"""

    name: str
    condition: Callable[[dict], bool]
    contents: list[ContentSpec]
