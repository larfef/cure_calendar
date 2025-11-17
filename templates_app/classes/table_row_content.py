class TableRowContent:
    """Handles line rendering logic for cure calendar"""

    def __init__(
        self,
        line_type,
        start,
        end=None,
        width=None,
        restart=False,
        product=False,
        stop=False,
    ):
        """
        Args:
            line_type: 'default', 'arrow', or 'stop'
            start: Integer from 0-7 indicating start day
            end: Integer from 0-7 indicating end day (optional)
            width: Width value (default: "100%")
            restart: Boolean indicating if this is a restart line
            stop: Boolean indicating if this is a stop line
        """
        self.type = line_type
        self.start = start
        self.product = product
        self.end = end
        self.width = width or "100%"
        self.restart = restart and self.type != "stop"
        self.stop = stop

    def get_context(self):
        """Returns pre-calculated values for template"""
        return {
            "type": self.type,
            "restart": self.restart,
            "product": self.product,
            "stop": self.stop,
            "width": self.width,
            "start": self.start,
            "end": self.end,
            "end_modulo": self._calculate_end_modulo(),
            # Pre-calculated styles
            "restart_style": self._get_restart_style() if self.restart else "",
            "stop_style": self._get_stop_style(),
            "line_style": self._get_line_style(),
            "margin_left": self._get_margin_left(),
            "padding_left": self._get_padding_left(),
        }

    def _calculate_end_modulo(self):
        """Calculate end_modulo value"""
        if self.end:
            return 7 - self.end

    def _get_restart_style(self):
        """Calculate inline style for restart indicator"""
        if self.start < 6:
            return f"margin-left: calc({self.start} * calc(var(--cell-width) + 1px))"
        else:
            return f"right: 1px;"

    def _get_stop_style(self):
        """Calculate inline style for stop indicator"""
        end_modulo = self._calculate_end_modulo()
        return f"margin-right: calc((var(--cell-width) * (7 - {self.end})) + {end_modulo}px)"

    def _get_margin_left(self):
        return f"margin-left: calc({self.start} * calc(var(--cell-width) + 1px))"

    def _get_padding_left(self):
        return f"padding-left: calc({self.start} * calc(var(--cell-width) + 1px))"

    def _get_line_style(self):
        """Calculate inline style for the line itself"""

        # styles = [f"width: {self.width}"]
        styles = [
            f"width: calc(var(--cell-width) * (7 - {self.start}) + 6px - {self.start}px)"
        ]

        if not self.product:
            # Add margin-left for all types except pause (pause handles its own positioning)
            if self.type != "pause":
                styles.append(
                    f"margin-left: calc({self.start} * calc(var(--cell-width) + 1px))"
                )

            # Add margin-right for stop type
            if self.type == "stop" and self.end:
                end_modulo = self._calculate_end_modulo()
                styles.append(
                    f"margin-right: calc((var(--cell-width) * (7 - {self.end})) + {end_modulo}px)"
                )

        return "; ".join(styles)
