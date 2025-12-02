from typing import List
from cure_calendar.constants.posology import (
    DAYS_PER_MONTH,
    DELAY_RULES,
    MAX_STARTING_DAYS,
    MONTH_BOUNDARY_ADJUSTMENT_WINDOW,
    MULTIPLE_PRODUCT_UNIT_RULES,
)
from cure_calendar.models.product import Product
from cure_calendar.types import (
    NormalizedProduct,
    ProductsData,
)


CORTISOL_PHASE_DURATION_DAYS = 28
MAX_DAYS_BETWEEN_PRODUCT_UNIT = 28


def _validate_and_get_posology_scheme(product: Product):
    """Validate and return the first posology scheme."""
    posology_scheme = product.posology_schemes.first()
    if not posology_scheme:
        raise ProductValidationError(
            f"Product '{product.label}' has no posology schemes"
        )

    if not posology_scheme.duration_value or posology_scheme.duration_value <= 0:
        raise ProductValidationError(
            f"Product '{product.label}' has invalid duration: "
            f"{posology_scheme.duration_value}"
        )

    return posology_scheme


def _validate_and_get_daily_quantity(product: Product, posology_scheme) -> float:
    """Validate and return total daily quantity."""
    total_daily_quantity = posology_scheme.get_total_daily_quantity()
    if not total_daily_quantity or total_daily_quantity <= 0:
        raise ProductValidationError(
            f"Product '{product.label}' has invalid total daily quantity: "
            f"{total_daily_quantity}"
        )
    return total_daily_quantity


def _validate_servings(product: Product):
    """Validate product servings."""
    if product.servings <= 0:
        raise ProductValidationError(
            f"Product '{product.label}' has invalid servings: {product.servings}"
        )


def adapter_products_data_normalized(
    products_data: ProductsData,
    cortisol_phase_duration: int = CORTISOL_PHASE_DURATION_DAYS,
) -> List[NormalizedProduct]:
    """
    Convert Product dict directly to normalized products in one pass.
    Combines adapter + normalization logic to avoid intermediate format.

    Args:
        product_dict: {product_id: Product} - Product objects already prefetched
        product_delays: {product_id: delay_value}
        cortisol_phase: Whether cortisol phase is active
        cortisol_phase_duration: Duration of cortisol phase

    Returns:
        List of fully normalized products ready for use
    """
    from django.utils.html import strip_tags

    normalized = []
    products_list = list(products_data.get("products").values())

    for product in products_list:
        # Validate and extract data in one pass
        posology_scheme = _validate_and_get_posology_scheme(product)
        total_daily_quantity = _validate_and_get_daily_quantity(
            product, posology_scheme
        )
        _validate_servings(product)

        # Compute delay (with cortisol phase consideration)
        base_delay = products_data.get("delays").get(product.id, 0)
        computed_delay = base_delay
        if products_data.get("cortisol_phase"):
            new_delay = DELAY_RULES[products_data.get("cortisol_phase")].get("id")
            if new_delay:
                computed_delay = new_delay
            else:
                computed_delay = base_delay + cortisol_phase_duration * (
                    product.phase == 2
                )

        second_unit = (
            product._has_exception(
                rule=lambda p: p in MULTIPLE_PRODUCT_UNIT_RULES["exceptions"]
            )
            and (
                product.id == 13
                and not any(other.id == 25 for other in products_list)
                or not products_data.get("cortisol_phase")
                and not products_data.get("delays").get(product.id)
            )
            or product._has_second_unit(
                rule=lambda p: p
                in MULTIPLE_PRODUCT_UNIT_RULES[products_data.get("cortisol_phase")][
                    product.phase
                ]["always"]
            )
        )

        total_daily_intakes_per_unit = int(product.servings / total_daily_quantity)

        pause_between_unit = (
            int(MAX_DAYS_BETWEEN_PRODUCT_UNIT - total_daily_intakes_per_unit)
            if total_daily_intakes_per_unit < MAX_STARTING_DAYS
            else 0
        )

        first_unit_end = computed_delay + total_daily_intakes_per_unit
        if first_unit_end in range(29, 36) and not second_unit:
            first_unit_end = 28

        second_unit_start = (
            computed_delay + pause_between_unit + total_daily_intakes_per_unit
        )

        if 29 <= second_unit_start < 37:
            second_unit_start = 29

        posology_end = (
            total_daily_intakes_per_unit * (second_unit + 1)
            + computed_delay
            + pause_between_unit
        )

        # Adjustement to gain space on A4 by stopping product at the end
        # of current month, so we avoid one extra line on following month
        for month_number in range(1, 4):  # months [1, 3]
            month_start = (DAYS_PER_MONTH + 1) * month_number  # day 29, 58, etc.
            month_end = month_start + MONTH_BOUNDARY_ADJUSTMENT_WINDOW

            if month_start <= posology_end < month_end:
                posology_end = DAYS_PER_MONTH * month_number

        normalized.append(
            {
                "id": product.id,
                "shopify_id": product.shopify_id,
                "label": strip_tags(product.label),
                "phase": product.phase,
                "posology": posology_scheme,
                "base_delay": base_delay,
                "servings": product.servings,
                "intake": posology_scheme.intakes.first(),
                "total_daily_quantity": total_daily_quantity,
                "total_daily_intakes_per_unit": total_daily_intakes_per_unit,
                "first_unit_start": computed_delay,
                "first_unit_end": first_unit_end,
                "second_unit": second_unit,
                "second_unit_start": second_unit_start,
                "pause_between_unit": pause_between_unit,
                "posology_end": posology_end,
            }
        )

    # Sort by delay
    normalized.sort(key=lambda p: p["first_unit_start"])
    return normalized


class ProductValidationError(Exception):
    """Raised when product data is invalid."""

    pass


class PosologyCalculator:
    def __init__(
        self,
        products: List[NormalizedProduct],
        cortisol_phase: bool = False,
        cortisol_phase_duration: int = CORTISOL_PHASE_DURATION_DAYS,
    ):
        if not products:
            raise ValueError("products cannot be None or empty")

        self.products = products
        self.cortisol_phase = cortisol_phase
        self.cortisol_phase_duration = cortisol_phase_duration * cortisol_phase

    def get_microbiote_phase_start(self):
        if self.cortisol_phase_duration > 0:
            # If there's a cortisol phase, find min delay among phase 2 products
            return min(
                (p for p in self.products if p["phase"] == 2),
                key=lambda p: p["first_unit_start"],
                default=min(self.products, key=lambda p: p["first_unit_start"]),
            )["first_unit_start"]
        else:
            # No cortisol phase, find min first_unit_start among all products
            return min(self.products, key=lambda p: p["first_unit_start"])[
                "first_unit_start"
            ]

    def get_cure_end_day(self):
        max_product = max(
            self.products,
            key=lambda p: p["posology_end"],
        )
        return max_product["posology_end"]

    def _compute_product_delay(self, phase: int, delay: int):
        new_delay = DELAY_RULES[self.cortisol_phase].get("id")
        if not new_delay:
            return delay + self.cortisol_phase_duration * (phase == 2)
        return new_delay

    def _product_second_unit_exceptions(self, id: int, delay: int, products: list):
        # 2 Mucopure units when Permea Intest isn't recommended
        if id == 13:
            return not any(p["id"] == 25 for p in products)
        else:
            return not self.cortisol_phase and not delay

    def _product_second_unit(self, id: int, phase: int, delay: int, products: list):
        if id in MULTIPLE_PRODUCT_UNIT_RULES["exceptions"]:
            return self._product_second_unit_exceptions(id, delay, products)

        # When product id is in always list
        # It means there is always a second product unit
        return id in MULTIPLE_PRODUCT_UNIT_RULES[self.cortisol_phase][phase]["always"]
