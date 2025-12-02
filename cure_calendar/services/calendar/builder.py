from dataclasses import dataclass
from cure_calendar.constants.posology import MAX_STARTING_DAYS
from cure_calendar.types import MonthSummary, NormalizedProduct
from cure_calendar.services.posology.calculator import PosologyCalculator
from cure_calendar.constants.calendar import CALENDAR_TEXT
from cure_calendar.services.calendar.collector import ContentCollector
from cure_calendar.services.calendar.materializer import RowMaterializer
from cure_calendar.utils.qrcode import qr_from_url


@dataclass
class CalendarContextBuilder:
    """
    Orchestrates calendar context building using two-phase architecture.

    Phase 1 (ContentCollector): Collects content for all products/weeks
    Phase 2 (RowMaterializer): Filters and builds template-ready rows
    """

    calculator: PosologyCalculator
    products: list[NormalizedProduct]
    cart_url: str

    def build(self) -> dict:
        """Main entry point - builds complete calendar context"""
        # Phase 1: Collect all content
        collector = ContentCollector(
            calculator=self.calculator,
            products=self.products,
        )

        # Phase 2: Materialize rows with filtering
        materializer = RowMaterializer(collector=collector)
        months = materializer.materialize()

        return self._create_context(months)

    def _create_context(self, months: list[MonthSummary]) -> dict:
        """Build final template context"""
        return {
            "text": CALENDAR_TEXT,
            "months": months,
            "legend": self._build_legend(),
            "phase_2": self._build_phase_2_section(),
        }

    def _build_phase_2_section(self) -> dict | None:
        """Build phase 2 section with QR code for reorder"""
        return {
            "qr_code": qr_from_url(self.cart_url),
            "enabled": self.cart_url,
        }

    def _build_legend(self) -> dict:
        """Build legend section for template"""
        return {
            "unit": [
                {
                    "icon": p["intake"].unit_icon,
                    "label": p["intake"].unit_label,
                }
                for i, p in enumerate(self.products)
                if not any(
                    p["intake"].unit_icon == prev["intake"].unit_icon
                    and p["intake"].unit_label == prev["intake"].unit_label
                    for prev in self.products[:i]
                )
            ],
            "time": [
                {
                    "icon": {
                        "src": p["intake"].time_of_day_icon,
                        "class": p["intake"].time_of_day_icon_class,
                    },
                    "label": p["intake"].time_of_day_label,
                    "bg_color": p["intake"].time_of_day_color,
                }
                for i, p in enumerate(self.products)
                if not any(
                    p["intake"].time_of_day == prev["intake"].time_of_day
                    for prev in self.products[:i]
                )
            ],
        }
