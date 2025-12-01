from dataclasses import dataclass
from typing import Any, Callable

from templates_app.types import SegmentContent, ContentType


@dataclass
class ContentSpec:
    """Specification for creating a SegmentContent - can use callables for dynamic values"""

    start: int | Callable[[dict], int]
    end: int | Callable[[dict], int]
    product: Any | Callable[[dict], Any] | None
    text: dict | Callable[[dict], dict] | None
    type_css: ContentType | Callable[[dict], ContentType]
    type_inline: ContentType | Callable[[dict], ContentType] = ContentType.CELL
    min_width_for_text: int = 2

    def resolve(self, ctx: dict) -> SegmentContent | None:
        """Resolve all callable values using context"""
        start = self.start(ctx) if callable(self.start) else self.start
        end = self.end(ctx) if callable(self.end) else self.end

        # Validation
        if start == end or end <= 0 or start < 0 or start >= 7 or start > end:
            return None

        text = self.text(ctx) if callable(self.text) else self.text
        if text:
            width_allows_text = (end - start) >= self.min_width_for_text
            text["enabled"] = text.get("enabled", True) and width_allows_text

        return {
            "start": start,
            "end": end,
            "product": self.product(ctx) if callable(self.product) else self.product,
            "text": text,
            "type": {
                "css": self.type_css(ctx) if callable(self.type_css) else self.type_css,
                "inline": self.type_inline(ctx)
                if callable(self.type_inline)
                else self.type_inline,
            },
        }
