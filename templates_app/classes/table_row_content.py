import copy
from typing import TypedDict
from enum import IntEnum


class TextType(IntEnum):
    DEFAULT = 0
    PRODUCT_LABEL = 1
    RESTART_PRODUCT = 2
    STOP_PRODUCT = 3
    PAUSE = 4


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
            TextType.PAUSE: "pause-container__text pause-text",
        }

        self.text_type_to_inline_style: dict = {
            TextType.STOP_PRODUCT: [self.get_margin_right],
            TextType.RESTART_PRODUCT: [self.prevent_text_overflow],
            TextType.PAUSE: [self.get_center_position],
        }

        self.content_type_to_css_style = {
            ContentType.GREEN_LINE: "line-green",
            ContentType.RED_LINE: "line-red",
            ContentType.ARROW: "line-green line-arrow-green",
            ContentType.PAUSE: "pause-line__dashed",
        }

        self.content_type_to_inline_style: dict = {
            ContentType.CELL: [self.get_width, self.get_margin_left],
        }

        self.contents = copy.deepcopy(contents)
        for i, content in enumerate(self.contents):
            content["_index"] = i
            content.update(
                {
                    "style": self._get_content_inline_style(
                        content,
                        self.content_type_to_inline_style.get(
                            content["type"]["inline"], []
                        ),
                    ),
                }
            )
            content.update(
                {"class": self.content_type_to_css_style.get(content["type"]["css"])}
            )
            text = content.get("text")
            if text and text.get("enabled"):
                content["text"].update(
                    {
                        "class": self.text_type_to_css_style.get(
                            content.get("text", []).get("type", TextType.DEFAULT)
                        )
                    }
                )
                content["text"].update(
                    {
                        "style": self._get_content_inline_style(
                            content,
                            self.text_type_to_inline_style.get(
                                content.get("text", []).get("type", TextType.DEFAULT)
                            ),
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
            # f"width: calc({self.base_width} * (7 - {content['start']})"
            # f" + 6px - {content['start']}px)"
            f"width: calc({self.base_width} *"
            f" ( -1 * {content.get('start', 0)} + {content.get('end', 7)})"
            f" + {content.get('end', 7)}px - {content.get('start', 0)}px)"
        )

    def get_margin_left(self, params) -> str:
        """Calculate left margin to account for gap from previous element"""
        index = params.get("_index", 0)
        if index == 0:
            return None

        prev_content = self.contents[index - 1]
        prev_end = prev_content["end"]
        gap = params["start"] - prev_end

        if gap > 0:
            return f"margin-left: calc({self.base_width} * {gap} + {gap}px)"
        return None

    def get_margin_right(self, content) -> str:
        return (
            f"margin-right: calc(({self.base_width} * (7 - {content['end']}))"
            f" + {7 - content['end']}px)"
        )

    def _get_padding_left(self, content):
        return f"padding-left: calc({content['start']} * calc({self.base_width} + 1px))"

    def get_center_position(self, content) -> str:
        """Calculate left position to center element between start and end"""
        midpoint = f"(({content['start']} + {content['end']}) / 2)"
        return (
            f"left: calc({self.base_width} * {midpoint}"
            f" + {midpoint} * 1px); transform: translateX(-50%)"
        )

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
