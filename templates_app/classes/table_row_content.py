import copy
from typing import TypedDict
from enum import IntEnum


class TextType(IntEnum):
    PRODUCT_LABEL = 0
    RESTART_PRODUCT = 1
    STOP_PRODUCT = 2


class ContentType(IntEnum):
    GREEN_LINE = 0
    RED_LINE = 1
    PAUSE = 2
    RESTART = 3
    ARROW = 4


class TextDict(TypedDict):
    value: str
    type: TextType
    enabled: bool


class ContentDict(TypedDict):
    end: int
    product: dict | None
    start: int
    text: TextDict | None
    type: str


class LineContent:
    """Handles line rendering logic for cure calendar"""

    def __init__(self, contents: list[ContentDict], time_col: bool = False):
        self.base_width = (
            "var(--cell-width)" if not time_col else "calc( 6 * var(--cell-width) / 7)"
        )

        self.text_type_to_css_style: dict = {
            TextType.PRODUCT_LABEL: "product-label",
            TextType.RESTART_PRODUCT: "line-container__restart",
            TextType.STOP_PRODUCT: "line-container__stop",
        }

        self.text_type_to_inline_style: dict = {
            TextType.STOP_PRODUCT: [self.get_margin_right],
            TextType.RESTART_PRODUCT: [self.prevent_text_overflow],
        }

        self.content_type_to_css_style = {
            ContentType.GREEN_LINE: "line-green",
            ContentType.RED_LINE: "line-red",
            ContentType.ARROW: "line-green line-arrow-green",
        }

        self.content_type_to_inline_style: dict = {
            ContentType.GREEN_LINE: [self.get_width],
            ContentType.RED_LINE: [self.get_width],
            ContentType.PAUSE: [self.get_width],
            ContentType.RESTART: [self.get_width],
        }

        self.contents = copy.deepcopy(contents)
        for content in self.contents:
            content.update(
                {
                    "style": self._get_content_inline_style(
                        content,
                        self.content_type_to_inline_style.get(content["type"], []),
                    ),
                }
            )
            content.update(
                {"class": self.content_type_to_css_style.get(content["type"])}
            )
            text = content.get("text")
            if text and text.get("enabled"):
                content["text"].update(
                    {"class": self.text_type_to_css_style.get(content["text"]["type"])}
                )
                content["text"].update(
                    {
                        "style": self._get_content_inline_style(
                            content,
                            self.text_type_to_inline_style.get(content["text"]["type"]),
                        )
                    }
                )

    def _get_content_inline_style(self, content, funcs):
        styles = []
        for func in funcs:
            val = func(content)
            if val:
                styles.append(val)
        return "; ".join(styles)

    def get_text_inline_style(self):
        pass

    def get_context(self):
        """Returns pre-calculated values for template"""
        pass
        return {
            "container": {"padding_left": self._get_padding_left(self.contents[0])},
            "contents": self.contents,
        }

    def get_width(self, content) -> str:
        return (
            f"width: calc({self.base_width} * (7 - {content['start']})"
            f" + 6px - {content['start']}px)"
        )

    def get_margin_right(self, content) -> str:
        return (
            f"margin-right: calc(({self.base_width} * (7 - {content['end']}))"
            f" + {7 - content['end']}px)"
        )

    def _get_padding_left(self, content):
        return f"padding-left: calc({content['start']} * calc({self.base_width} + 1px))"

    def prevent_text_overflow(self, content) -> str:
        if content["start"] >= 5:
            return "right: 1px"


class TableRowContent:
    """Handles line rendering logic for cure calendar"""

    def __init__(
        self,
        line_type,
        start=0,
        end=7,
        restart=0,
        text=None,
        time_col=False,
        product=False,
        product_label=False,
    ):
        """
        Args:
            line_type: 'default', 'arrow', or 'stop'
            start: Integer from 0-7 indicating start day
            end: Integer from 0-7 indicating end day (optional)
            stop: Boolean indicating if this is a stop line
        """
        self.type = line_type
        self.start = start
        self.end = end
        self.restart = restart if restart > end and restart <= 7 else 0
        self.text = text
        self.cell_width = (
            "var(--cell-width)" if not time_col else "calc( 6 * var(--cell-width) / 7)"
        )
        self.product = product
        self.product_label = product_label

    def get_context(self):
        """Returns pre-calculated values for template"""
        return {
            "type": self.type,
            "text": self.text,
            "product": self.product,
            "product_label": self.product_label,
            "start": self.start,
            "end": self.end,
            # Pre-calculated styles
            "style": {
                "stop": self._stop_margin_right(),
                "restart": self._prevent_text_overflow(),
                "line": self._get_line_style(),
                "padding_left": self._get_padding_left(),
            },
        }

    def _prevent_text_overflow(self):
        """Prevent text overflow from table"""
        if self.start >= 5:
            return "right: 1px;"

    def _stop_margin_right(self):
        """Calculate inline margin right for stop indicator"""
        return f"margin-right: calc(({self.cell_width} * (7 - {self.end})) + {7 - self.end}px)"

    def _get_padding_left(self):
        # return f"padding-left: calc({self.start} * calc(var(--cell-width) + 1px))"
        return f"padding-left: calc({self.start} * calc({self.cell_width} + 1px))"

    def _get_line_style(self):
        """Calculate inline style for the line itself"""
        styles = [
            f"width: calc({self.cell_width} * (7 - {self.start}) + 6px - {self.start}px)"
        ]
        # Add margin-right for stop type
        if self.type == "stop" and self.end:
            styles.append(self._stop_margin_right())

        return "; ".join(styles)
