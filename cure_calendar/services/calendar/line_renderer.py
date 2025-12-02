import copy

from cure_calendar.types import SegmentContent, ContentType, TextType


class LineRenderer:
    """Handles line rendering logic for cure calendar"""

    def __init__(self, contents: list[SegmentContent], time_col: bool = False):
        self.base_width = (
            "var(--cell-width)" if not time_col else "calc( 6 * var(--cell-width) / 7)"
        )

        self.text_type_to_css_style: dict = {
            TextType.PRODUCT_LABEL: "product-label--layout product-label",
            TextType.RESTART_PRODUCT: "line-container__restart",
            TextType.STOP_PRODUCT: "line-container__stop",
            TextType.PAUSE: "pause-container__text pause-text",
            TextType.FINISH_PRODUCT: "cell-content__container--text-finish",
        }

        self.text_type_to_inline_style: dict = {
            TextType.STOP_PRODUCT: [self.get_margin_right],
            TextType.RESTART_PRODUCT: [self.prevent_text_overflow],
            TextType.PAUSE: [self.get_center_position],
            TextType.FINISH_PRODUCT: [self.get_center_position],
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
        if not funcs:
            return
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
        start = content["start"]
        end = content["end"]
        midpoint = (start + end) // 2
        return (
            f"left: calc({self.base_width} * {(start + end) / 2} + {midpoint}px); "
            f"transform: translateX(-50%)"
        )

    def prevent_text_overflow(self, content) -> str:
        if content["start"] >= 6:
            return "right: 1px"
        return f"padding-left: calc({content['start']} * calc({self.base_width} + 1px))"
