from cure_calendar.constants.posology import LAST_WEEK_TO_DISPLAY
from cure_calendar.services.rules.base import Rule
from cure_calendar.services.rules.specs import ContentSpec
from cure_calendar.types import ContentType, NormalizedProduct, TextType


def get_rules(product: NormalizedProduct) -> list[Rule]:
    """Define rules for a product. Order matters - first match wins."""
    return [
        Rule(
            name="product_starts_this_week",
            condition=lambda c: (
                c["first_unit_start"] < c["week_end"]
                and c["first_unit_start"] >= c["week_start"]
            ),
            contents=[
                ContentSpec(
                    start=lambda c: (
                        c["first_unit_start"] - c["week_start"]
                        if c["first_unit_start"] > 28 or c["first_unit_start"] < 22
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
            name="product_continues_during_week_12",
            condition=lambda c, p=product: (
                c["week_index"] == LAST_WEEK_TO_DISPLAY - 1
                and p["posology_end"] > c["week_end"]
            ),
            contents=[
                ContentSpec(
                    start=0,
                    end=7,
                    product=None,
                    text=lambda p=product: (
                        {
                            "value": f"{p['label']} Terminer la boite",
                            "type": TextType.FINISH_PRODUCT,
                            "enabled": True,
                        }
                    ),
                    type_css=ContentType.GREEN_LINE,
                )
            ],
        ),
        Rule(
            name="product_pause_between_units",
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
                    text=lambda c, p=product: {
                        # "value": f"{p['label']} : Terminer boite 1"
                        # if not c["week_index"] % 3 and not p["pause_between_unit"]
                        # else f" Arrêter {p['label']}",
                        "value": f" Arrêter {p['label']}"
                        if c["week_index"] % 3 or p["pause_between_unit"]
                        else f"{p['label']} : Terminer boite 1",
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
                        c["first_unit_end"] - c["week_start"] + c["pause_between_unit"],
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
                        c["first_unit_end"] - c["week_start"] + c["pause_between_unit"],
                    ),
                    end=7,
                    product=None,
                    text=lambda c, p=product: {
                        "value": f"{p['label']} : Démarrer boite 2",
                        "type": TextType.RESTART_PRODUCT,
                        "enabled": True,
                    },
                    type_css=ContentType.GREEN_LINE,
                ),
            ],
        ),
        Rule(
            name="product_restart_this_week",
            condition=lambda c: (
                c["second_unit"]
                and c["second_unit_start"] >= c["week_start"]
                and c["second_unit_start"] < c["week_end"]
            ),
            contents=[
                ContentSpec(
                    start=0,
                    end=7,
                    product=None,
                    text=lambda c, p=product: {
                        "value": f"{'Recommencer' if c['pause_between_unit'] else 'Continuer'} {p['label']}",
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
                    text=lambda c, p=product: (
                        {
                            "value": p["label"],
                            "type": TextType.PRODUCT_LABEL,
                            "enabled": True,
                        }
                        if c["is_first_week"]
                        else None
                    ),
                    type_css=lambda c: ContentType.ARROW
                    if c["is_last_week"]
                    else ContentType.GREEN_LINE,
                )
            ],
        ),
        Rule(
            name="product_ends_this_week",
            condition=lambda c: c["week_start"] < c["posology_end"]
            and c["posology_end"] <= c["week_end"],
            contents=[
                ContentSpec(
                    start=0,
                    end=lambda c: 7 - (c["week_end"] - c["posology_end"]),
                    product=None,
                    text=lambda c, p=product: {
                        "value": f"Arrêter {p['label']}",
                        "type": TextType.STOP_PRODUCT,
                        "enabled": True,
                    },
                    type_css=ContentType.RED_LINE,
                    min_width_for_text=1,
                )
            ],
        ),
        Rule(
            name="product_not_started",
            condition=lambda c: c["first_unit_start"] >= c["week_end"],
            contents=[],
        ),
        Rule(
            name="product_already_ended",
            condition=lambda c: c["posology_end"] < c["week_start"],
            contents=[],
        ),
    ]
