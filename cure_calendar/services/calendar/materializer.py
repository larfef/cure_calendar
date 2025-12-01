from dataclasses import dataclass, field

from cure_calendar.services.calendar.line_renderer import LineRenderer
from cure_calendar.constants.calendar import TIME_SLOTS
from cure_calendar.services.calendar.collector import ContentCollector
from cure_calendar.types import (
    MonthSummary,
    WeekSchedule,
    TimeSlotContent,
    NumLine,
)
from cure_calendar.types import (
    ContentMap,
    MonthIndex,
    WeekIndex,
    ProductId,
    TimeSlot,
)


@dataclass
class RowMaterializer:
    """
    Phase 2: Transforms ContentMap into template-ready MonthSummary structures.

    Responsibilities:
    - Filter out products with no content across entire month
    - Build rows only for active products
    - Apply LineContent transformation for styling
    - Calculate num_lines and enabled flags
    """

    collector: ContentCollector
    _content_map: ContentMap = field(default=None, init=False)

    def materialize(self) -> list[MonthSummary]:
        """Main entry point - returns list of months ready for templates"""
        self._content_map = self.collector.collect()

        months: list[MonthSummary] = []

        for month_index in sorted(self._content_map.keys()):
            month = self._build_month(month_index)
            months.append(month)

        return months

    def _build_month(self, month_index: MonthIndex) -> MonthSummary:
        """Build a complete month structure with filtered rows"""
        # Determine number of weeks in this month
        num_weeks = self._get_weeks_in_month(month_index)

        # Pre-compute active products for each time slot
        active_products: dict[TimeSlot, list[ProductId]] = {}
        for slot in TIME_SLOTS:
            active_products[slot] = self.collector.get_active_products(
                month_index, slot
            )

        # Build weeks
        weeks: list[WeekSchedule] = []
        for week_in_month in range(num_weeks):
            week = self._build_week(
                month_index=month_index,
                week_in_month=week_in_month,
                active_products=active_products,
            )
            weeks.append(week)

        # Calculate num_lines (max rows per slot across all weeks)
        num_lines: NumLine = {
            slot: max((len(week[slot]["rows"]) for week in weeks), default=0)
            for slot in TIME_SLOTS
        }

        # Update enabled flags based on num_lines
        for week in weeks:
            for slot in TIME_SLOTS:
                week[slot]["enabled"] = num_lines[slot] > 0

        return {
            "weeks": weeks,
            "num_lines": num_lines,
        }

    def _build_week(
        self,
        month_index: MonthIndex,
        week_in_month: WeekIndex,
        active_products: dict[TimeSlot, list[ProductId]],
    ) -> WeekSchedule:
        """Build a single week with rows for active products only"""
        global_week_index = month_index * 4 + week_in_month

        week: WeekSchedule = {
            "morning": self._build_time_slot(
                month_index, week_in_month, "morning", active_products["morning"]
            ),
            "evening": self._build_time_slot(
                month_index, week_in_month, "evening", active_products["evening"]
            ),
            "mixed": self._build_time_slot(
                month_index, week_in_month, "mixed", active_products["mixed"]
            ),
            "display": {
                "time_column": week_in_month == 0,  # First week of month
                "table_header": month_index == 0,  # First month only
            },
            "number": global_week_index + 1,
        }

        return week

    def _build_time_slot(
        self,
        month_index: MonthIndex,
        week_in_month: WeekIndex,
        slot: TimeSlot,
        active_product_ids: list[ProductId],
    ) -> TimeSlotContent:
        """Build rows for a time slot, including only active products"""
        rows = []
        is_first_week = week_in_month == 0

        for product_id in active_product_ids:
            content = self.collector.get_content(
                month_index, slot, product_id, week_in_month
            )

            if content is not None and len(content) > 0:
                # Transform through LineContent for styling
                row = LineRenderer(
                    contents=content, time_col=is_first_week
                ).get_context()
                rows.append(row)
            else:
                # Empty placeholder for alignment within active products
                rows.append("")

        return {
            "enabled": True,  # Will be updated after all weeks are built
            "rows": rows,
        }

    def _get_weeks_in_month(self, month_index: MonthIndex) -> int:
        """Determine how many weeks exist in this month (may be less than 4 for last month)"""
        if month_index not in self._content_map:
            return 0

        # Find max week index across all time slots and products
        max_week = -1
        for slot_data in self._content_map[month_index].values():
            for product_weeks in slot_data.values():
                for week_idx in product_weeks.keys():
                    max_week = max(max_week, week_idx)

        return max_week + 1 if max_week >= 0 else 0
