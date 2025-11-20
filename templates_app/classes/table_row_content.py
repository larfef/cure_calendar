class TableRowContent:
    """Handles line rendering logic for cure calendar"""

    def __init__(
        self,
        line_type,
        start=0,
        end=7,
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
