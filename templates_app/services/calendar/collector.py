import math
from dataclasses import dataclass, field

from templates_app.services.rules.product_rules import get_rules
from templates_app.types import SegmentContent
from templates_app.types import (
    ContentMap,
    MonthIndex,
    WeekIndex,
    NormalizedProduct,
    ProductId,
    TimeSlot,
)
from templates_app.services.posology.calculator import PosologyCalculator


N_DAYS_WEEK = 7


@dataclass
class ContentCollector:
    """
    Phase 1: Collects content for all products across all weeks.

    Stores results in a ContentMap structure, keyed by:
    month → time_slot → product_id → week_index → content (or None)
    """

    calculator: PosologyCalculator
    products: list[NormalizedProduct]
    _content_map: ContentMap = field(default_factory=dict, init=False)

    def collect(self) -> ContentMap:
        """Main entry point - collects all content and returns the map"""
        total_weeks = math.ceil(self.calculator.get_cure_end_day() / N_DAYS_WEEK)

        for week_index in range(total_weeks):
            self._process_week(week_index)

        return self._content_map

    def _process_week(self, week_index: int) -> None:
        """Process all products for a single week"""
        month_index = week_index // 4
        week_in_month = week_index % 4

        # Ensure month structure exists
        self._ensure_month_exists(month_index)

        for product in self.products:
            self._collect_product_content(
                product, week_index, month_index, week_in_month
            )

    def _collect_product_content(
        self,
        product: NormalizedProduct,
        week_index: int,
        month_index: MonthIndex,
        week_in_month: WeekIndex,
    ) -> None:
        """Evaluate rules for a product and store content in map"""
        week_start = week_index * N_DAYS_WEEK
        week_end = (week_index + 1) * N_DAYS_WEEK

        ctx = {
            **product,
            "week_index": week_index,
            "week_start": week_start,
            "week_end": week_end,
            "is_first_week": week_index % 4 == 0,
            "is_last_week": week_index % 4 == 3,
        }

        rules = get_rules(product)
        time_slot: TimeSlot = ctx["posology"].day_time
        product_id: ProductId = product["id"]

        # Ensure nested structure exists
        if time_slot not in self._content_map[month_index]:
            self._content_map[month_index][time_slot] = {}
        if product_id not in self._content_map[month_index][time_slot]:
            self._content_map[month_index][time_slot][product_id] = {}

        # Evaluate rules and store result
        content = self._evaluate_rules(rules, ctx)
        self._content_map[month_index][time_slot][product_id][week_in_month] = content

    def _evaluate_rules(
        self, rules: list[Rule], ctx: dict
    ) -> list[SegmentContent] | None:
        """
        Find first matching rule and resolve its content.

        Returns:
            - list[SegmentContent]: Valid content array
            - None: No content for this week (product not started, ended, etc.)
        """
        for rule in rules:
            if rule.condition(ctx):
                if not rule.contents:
                    return None  # Explicit "no content" rule

                content_array = [
                    resolved
                    for resolved in (spec.resolve(ctx) for spec in rule.contents)
                    if resolved is not None
                ]

                return content_array if content_array else None

        return None  # No rule matched

    def _ensure_month_exists(self, month_index: MonthIndex) -> None:
        """Initialize month structure if needed"""
        if month_index not in self._content_map:
            self._content_map[month_index] = {}

    # def _get_rules(self, product: NormalizedProduct) -> list[Rule]:
    #     """Define rules for a product. Order matters - first match wins."""
    #     return [
    #         Rule(
    #             name="product_starts_this_week",
    #             condition=lambda c: (
    #                 c["first_unit_start"] < c["week_end"]
    #                 and c["first_unit_start"] >= c["week_start"]
    #             ),
    #             contents=[
    #                 ContentSpec(
    #                     start=lambda c: (
    #                         c["first_unit_start"] - c["week_start"]
    #                         if c["first_unit_start"] > 28 or c["first_unit_start"] < 22
    #                         else 0
    #                     ),
    #                     end=7,
    #                     product=product,
    #                     text=None,
    #                     type_css=lambda c: ContentType.ARROW
    #                     if c["is_last_week"]
    #                     else ContentType.GREEN_LINE,
    #                 )
    #             ],
    #         ),
    #         Rule(
    #             name="product_pause_between_units",
    #             condition=lambda c: (
    #                 c["second_unit"]
    #                 and c["first_unit_end"] < c["week_end"] + 1
    #                 and (c["first_unit_end"] + c["pause_between_unit"])
    #                 > c["week_start"] + 1
    #             ),
    #             contents=[
    #                 ContentSpec(
    #                     start=lambda c: max(0, c["first_unit_start"] - c["week_start"]),
    #                     end=lambda c: c["first_unit_end"] - c["week_start"],
    #                     product=None,
    #                     text=lambda c: {
    #                         "value": "Fin du pot 1",
    #                         "type": TextType.STOP_PRODUCT,
    #                         "enabled": True,
    #                     },
    #                     type_css=ContentType.RED_LINE,
    #                     min_width_for_text=1,
    #                 ),
    #                 ContentSpec(
    #                     start=lambda c: max(0, c["first_unit_end"] - c["week_start"]),
    #                     end=lambda c: min(
    #                         7,
    #                         c["first_unit_end"]
    #                         - c["week_start"]
    #                         + c["pause_between_unit"],
    #                     ),
    #                     product=None,
    #                     text=lambda c: {
    #                         "value": "Pause",
    #                         "type": TextType.PAUSE,
    #                         "enabled": True,
    #                     },
    #                     type_css=ContentType.PAUSE,
    #                 ),
    #                 ContentSpec(
    #                     start=lambda c: min(
    #                         7,
    #                         c["first_unit_end"]
    #                         - c["week_start"]
    #                         + c["pause_between_unit"],
    #                     ),
    #                     end=7,
    #                     product=None,
    #                     text=lambda c: {
    #                         "value": "Démarrer pot 2",
    #                         "type": TextType.RESTART_PRODUCT,
    #                         "enabled": True,
    #                     },
    #                     type_css=ContentType.GREEN_LINE,
    #                 ),
    #             ],
    #         ),
    #         Rule(
    #             name="product_restart_this_week",
    #             condition=lambda c: (
    #                 c["first_unit_start"] > 1
    #                 and c["second_unit_start"] >= c["week_start"]
    #                 and c["second_unit_start"] < c["week_end"]
    #             ),
    #             contents=[
    #                 ContentSpec(
    #                     start=0,
    #                     end=7,
    #                     product=None,
    #                     text=lambda c, p=product: {
    #                         "value": f"{'Recommencer' if c['pause_between_unit'] else 'Continuer'} {p['label']}",
    #                         "type": TextType.RESTART_PRODUCT,
    #                         "enabled": True,
    #                     },
    #                     type_css=lambda c: ContentType.GREEN_LINE,
    #                 )
    #             ],
    #         ),
    #         Rule(
    #             name="product_continues_through_week",
    #             condition=lambda c: c["posology_end"] > c["week_end"]
    #             and c["first_unit_start"] < c["week_start"],
    #             contents=[
    #                 ContentSpec(
    #                     start=0,
    #                     end=7,
    #                     product=None,
    #                     text=lambda c, p=product: (
    #                         {
    #                             "value": p["label"],
    #                             "type": TextType.PRODUCT_LABEL,
    #                             "enabled": True,
    #                         }
    #                         if c["is_first_week"]
    #                         else None
    #                     ),
    #                     type_css=lambda c: ContentType.ARROW
    #                     if c["is_last_week"]
    #                     else ContentType.GREEN_LINE,
    #                 )
    #             ],
    #         ),
    #         Rule(
    #             name="product_ends_this_week",
    #             condition=lambda c: c["week_start"] < c["posology_end"]
    #             and c["posology_end"] <= c["week_end"],
    #             contents=[
    #                 ContentSpec(
    #                     start=0,
    #                     end=lambda c: 7 - (c["week_end"] - c["posology_end"]),
    #                     product=None,
    #                     text=lambda c, p=product: {
    #                         "value": f"Arrêter {p['label']}",
    #                         "type": TextType.STOP_PRODUCT,
    #                         "enabled": True,
    #                     },
    #                     type_css=ContentType.RED_LINE,
    #                     min_width_for_text=1,
    #                 )
    #             ],
    #         ),
    #         Rule(
    #             name="product_not_started",
    #             condition=lambda c: c["first_unit_start"] >= c["week_end"],
    #             contents=[],
    #         ),
    #         Rule(
    #             name="product_already_ended",
    #             condition=lambda c: c["posology_end"] < c["week_start"],
    #             contents=[],
    #         ),
    #     ]

    # === Access Methods for Phase 2 ===

    def get_active_products(self, month: MonthIndex, slot: TimeSlot) -> list[ProductId]:
        """Get product IDs that have content in at least one week of the month"""
        if month not in self._content_map or slot not in self._content_map[month]:
            return []

        return [
            pid
            for pid, weeks in self._content_map[month][slot].items()
            if any(content is not None for content in weeks.values())
        ]

    def get_content(
        self, month: MonthIndex, slot: TimeSlot, product_id: ProductId, week: WeekIndex
    ) -> list[SegmentContent] | None:
        """Get content for a specific product/week, or None if no content"""
        try:
            return self._content_map[month][slot][product_id][week]
        except KeyError:
            return None
