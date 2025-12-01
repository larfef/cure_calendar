import math
from dataclasses import dataclass
from typing import Callable, Any

import qrcode
from templates_app.classes.line_content import (
    ContentDict,
    ContentType,
    LineContent,
    TextType,
)
from templates_app.constants.posology_constants import MAX_STARTING_DAYS
from templates_app.types.calendar import (
    WeekSchedule,
    MonthSummary,
)
from templates_app.classes.posology_calculation_model import PosologyCalculationModel
from templates_app.constants.calendar_constants import CALENDAR_TEXT, DAY_TIME_SLOTS
from templates_app.types.product import NormalizedProduct


@dataclass
class ContentSpec:
    """Specification for creating a ContentDict - can use callables for dynamic values"""

    start: int | Callable[[dict], int]  # Can be static or computed
    end: int | Callable[[dict], int]
    product: Any | Callable[[dict], Any] | None
    text: dict | Callable[[dict], dict] | None
    type_css: ContentType | Callable[[dict], ContentType]
    type_inline: ContentType | Callable[[dict], ContentType] = ContentType.CELL
    min_width_for_text: int = 2

    def resolve(self, ctx: dict) -> ContentDict:
        """Resolve all callable values using context"""
        start = self.start(ctx) if callable(self.start) else self.start
        end = self.end(ctx) if callable(self.end) else self.end

        # VALIDATION RULES
        if start == end:  # Zero-width content
            return None
        if end <= 0:  # Invalid end
            return None
        if start < 0:  # Start before week
            return None
        if start >= 7:  # Start after week
            return None
        if start > end:  # Invalid range
            return None

        text = self.text(ctx) if callable(self.text) else self.text

        if text:
            user_enabled = text.get("enabled", True)

            # Check width constraint
            width_allows_text = (end - start) >= self.min_width_for_text

            # Final enabled = user condition AND width check
            text["enabled"] = user_enabled and width_allows_text

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


@dataclass
class Rule:
    """A rule for determining what content to add to a week"""

    name: str
    condition: Callable  # Returns bool
    contents: list[ContentSpec]  # Returns list[ContentDict]


def qr_from_url(url, box_size=5):
    qr = qrcode.QRCode(
        image_factory=qrcode.image.svg.SvgPathImage,
        box_size=box_size,
        border=0,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image()
    qr_img = qr_img.to_string(encoding="unicode")

    return qr_img


@dataclass
class CalendarContextBuilder:
    """Builds calendar context for template rendering"""

    NB_DAY = 7
    MONTH_DAY = 4 * NB_DAY

    calculator: PosologyCalculationModel
    products: NormalizedProduct
    cart_url: str

    def build(self) -> dict:
        """Main entry point - builds complete calendar context"""

        self.months: list[MonthSummary] = []

        total_weeks = math.ceil(
            self.calculator.get_microbiote_phase_end() / self.NB_DAY
        )

        for week_index in range(total_weeks):
            self._process_week(week_index)

        return self._create_context()

    def _process_week(self, week_index: int) -> None:
        """Process a single week and add to appropriate month"""
        current_month = week_index // 4
        current_week = week_index % 4

        # Ensure month exists
        self._ensure_month_exists(current_month)

        # Create and populate week
        week = self._create_empty_week(
            week_index=week_index,
            time_column=current_week == 0,
            table_header=current_month == 0,
        )

        # Add content for each product
        for product in self.products:
            self._add_product_to_week(product, week, week_index)

        # Add week to month
        self.months[current_month]["weeks"].append(week)

        # Update line counts
        self._update_month_line_counts(current_month)
        self._update_week_enabled_slots(week, current_month)

        pass

    def _create_empty_week(
        self, week_index: int, time_column: bool = False, table_header: bool = False
    ) -> WeekSchedule:
        """Factory for creating properly typed empty week"""
        return {
            "morning": {"enabled": True, "rows": []},
            "evening": {"enabled": True, "rows": []},
            "mixed": {"enabled": True, "rows": []},
            "display": {
                "time_column": time_column,
                "table_header": table_header,
            },
            "number": week_index + 1,
        }

    def _add_product_to_week(
        self, product: NormalizedProduct, week: WeekSchedule, week_index: int
    ) -> None:
        """Add product schedule to appropriate time slot in week"""
        week_start = week_index * self.NB_DAY
        week_end = (week_index + 1) * self.NB_DAY

        ctx = {
            **product,
            "week_index": week_index,
            "week_start": week_start,
            "week_end": week_end,
            "is_first_week": week_index % 4 == 0,
            "is_last_week": week_index % 4 == 3,
        }

        rules = [
            Rule(
                name="product_starts_this_week",
                condition=lambda c: c["first_unit_start"] < c["week_end"]
                and c["first_unit_start"] >= c["week_start"],
                contents=[
                    ContentSpec(
                        start=lambda c: (
                            c["first_unit_start"] - c["week_start"]
                            if (
                                c["first_unit_start"] > 28 or c["first_unit_start"] < 22
                            )
                            else 0
                        ),
                        end=7,
                        product=product,
                        text=None,
                        type_css=lambda c: ContentType.ARROW
                        if c["is_last_week"]
                        else ContentType.GREEN_LINE,
                    )
                ],
            ),
            Rule(
                name="product_pause_between_units",
                # Ranges [A, B] where A < B
                # and [C, D] where C < D overlap
                # if A < D and B > C
                condition=lambda c: (
                    c["second_unit"]
                    and c["first_unit_end"] < c["week_end"] + 1
                    and (c["first_unit_end"] + c["pause_between_unit"])
                    > c["week_start"] + 1
                ),
                contents=[
                    ContentSpec(
                        start=lambda c: max(0, c["first_unit_start"] - c["week_start"]),
                        end=lambda c: c["first_unit_end"] - c["week_start"],
                        product=None,
                        text=lambda c: {
                            "value": "Fin du pot 1",
                            "type": TextType.STOP_PRODUCT,
                            "enabled": True,
                        },
                        type_css=ContentType.RED_LINE,
                        min_width_for_text=1,
                    ),
                    ContentSpec(
                        start=lambda c: max(0, c["first_unit_end"] - c["week_start"]),
                        end=lambda c: min(
                            7,
                            c["first_unit_end"]
                            - c["week_start"]
                            + c["pause_between_unit"],
                        ),
                        product=None,
                        text=lambda c: {
                            "value": "Pause",
                            "type": TextType.PAUSE,
                            "enabled": True,
                        },
                        type_css=ContentType.PAUSE,
                    ),
                    ContentSpec(
                        start=lambda c: min(
                            7,
                            c["first_unit_end"]
                            - c["week_start"]
                            + c["pause_between_unit"],
                        ),
                        end=7,
                        product=None,
                        text=lambda c: {
                            "value": "Démarrer pot 2",
                            "type": TextType.RESTART_PRODUCT,
                            "enabled": True,
                        },
                        type_css=ContentType.GREEN_LINE,
                    ),
                ],
            ),
            Rule(
                name="product_restart_this_week",
                condition=lambda c: c["first_unit_start"] > 1
                and c["second_unit_start"] >= c["week_start"]
                and c["second_unit_start"] < c["week_end"],
                contents=[
                    ContentSpec(
                        start=0,
                        end=7,
                        product=None,
                        text=lambda c: {
                            "value": f"{'Recommencer' if c['pause_between_unit'] else 'Continuer'} {product['label']}",
                            "type": TextType.RESTART_PRODUCT,
                            "enabled": True,
                        },
                        type_css=lambda c: ContentType.GREEN_LINE,
                    )
                ],
            ),
            Rule(
                name="product_continues_through_week",
                condition=lambda c: c["posology_end"] > c["week_end"]
                and c["first_unit_start"] < c["week_start"],
                contents=[
                    ContentSpec(
                        start=0,
                        end=7,
                        product=None,
                        text=lambda c: {
                            "value": product["label"],
                            "type": TextType.PRODUCT_LABEL,
                            "enabled": True,
                        }
                        if c["is_first_week"]
                        else None,
                        type_css=lambda c: ContentType.ARROW
                        if c["is_last_week"]
                        else ContentType.GREEN_LINE,
                    )
                ],
            ),
            Rule(
                name="product_ends_this_week",
                # condition=lambda c: c["posology_end"] <= c["week_end"]
                # and c["posology_end"] > c["week_start"],
                condition=lambda c: c["week_start"] < c["posology_end"]
                and c["posology_end"] <= c["week_end"],
                contents=[
                    ContentSpec(
                        start=0,
                        end=lambda c: 7 - (c["week_end"] - c["posology_end"]),
                        product=None,
                        text=lambda c: {
                            "value": f"Arrêter {product['label']}",
                            "type": TextType.STOP_PRODUCT,
                            "enabled": True,
                        },
                        type_css=ContentType.RED_LINE,
                        min_width_for_text=1,
                    )
                ],
            ),
            # Rule(
            #     name="empty_slot_same_month",
            #     condition=lambda c: (
            #         (c["week_end"] // (self.MONTH_DAY + 1))
            #         == (c["posology_end"] // (self.MONTH_DAY + 1))
            #     ),
            #     contents=[],  # Empty content array
            # ),
            Rule(
                name="product_not_started",
                condition=lambda c: c["first_unit_start"] >= c["week_end"],
                contents=[],  # Empty content array
            ),
            Rule(
                name="product already ended",
                condition=lambda c: c["posology_end"] < c["week_start"],
                contents=[],
            ),
        ]

        # Debug Statement
        if week_index == 4:
            pass

        day_time = ctx["posology"].day_time
        # Execute first matching rule
        for rule in rules:
            if rule.condition(ctx):
                if rule.contents:
                    # Resolve all ContentSpecs to actual ContentDicts
                    content_array = [
                        resolved
                        for resolved in (spec.resolve(ctx) for spec in rule.contents)
                        if resolved is not None
                    ]
                    if content_array:  # Only render if we have valid content
                        line_content = LineContent(
                            contents=content_array, time_col=ctx["is_first_week"]
                        ).get_context()
                        week[day_time]["rows"].append(line_content)
                    else:
                        week[day_time]["rows"].append("")  # All content was invalid
                else:
                    # Empty content
                    week[day_time]["rows"].append("")
                break

    def _update_month_line_counts(self, month_index: int) -> None:
        """Update maximum line counts for each time slot in month"""
        month = self.months[month_index]
        for time_slot in DAY_TIME_SLOTS:
            month["num_lines"][time_slot] = max(
                len(week[time_slot]["rows"]) for week in month["weeks"]
            )
        pass

    def _update_week_enabled_slots(self, week: WeekSchedule, month_index: int) -> None:
        """Enable/disable time slots based on content"""
        month = self.months[month_index]
        for time_slot in DAY_TIME_SLOTS:
            week[time_slot]["enabled"] = month["num_lines"][time_slot] != 0
        pass

    def _ensure_month_exists(self, month_index: int) -> None:
        """Create month structure if it doesn't exist"""
        while len(self.months) <= month_index:
            self.months.append(
                {"weeks": [], "num_lines": {"morning": 0, "evening": 0, "mixed": 0}}
            )

    def _create_context(self) -> dict:
        """Build final template context"""
        return {
            "text": CALENDAR_TEXT,
            "months": self.months,
            "legend": self._build_legend(),
            "phase_2": self._build_phase_2_section(),
        }

    def _build_phase_2_section(self) -> dict:
        if not self.cart_url:
            return None
        return {
            "qr_code": qr_from_url(self.cart_url),
            "products": [
                p["label"]
                for p in self.products
                if p["first_unit_start"] >= MAX_STARTING_DAYS - 1
                or p["second_unit"]
                and p["second_unit_start"] >= MAX_STARTING_DAYS - 1
            ],
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
