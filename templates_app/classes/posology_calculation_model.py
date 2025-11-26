import math
from typing import Dict, List, Union

from django.utils.html import strip_tags
from templates_app.constants.posology_constants import (
    DELAY_RULES,
    MULTIPLE_PRODUCT_UNIT_RULES,
)
from templates_app.models.product import Product
from templates_app.types.product import A5Product, AdaptedA5Product


CORTISOL_PHASE_DURATION_DAYS = 28
MAX_DAYS_BETWEEN_PRODUCT_UNIT = 28


def adapter_a5_product(products: List[A5Product]) -> List[AdaptedA5Product]:
    """Convert A5Product to AdaptedA5Product by fetching posology schemes from DB."""
    product_labels = [product["label"] for product in products]

    # Create dict mapping label -> Product instance (for lookup)
    product_lookup = {
        v.label: v
        for v in Product.objects.filter(label__in=product_labels).prefetch_related(
            "posology_schemes"
        )
    }

    new_products: List[AdaptedA5Product] = []
    for product in products:
        adapted_product = product_lookup.get(product["label"])

        if adapted_product:
            new_products.append(
                {
                    "id": adapted_product.id,
                    "label": product["label"],
                    "nutrients": product.get("nutrients"),
                    "posology": adapted_product.posology_schemes.all(),  # QuerySet
                    "servings": adapted_product.servings,
                    "delay": product["delay"],
                    "phase": product["phase"],
                }
            )

    return new_products


class ProductValidationError(Exception):
    """Raised when product data is invalid."""

    pass


class PosologyCalculationModel:
    def __init__(
        self,
        products: Union[List[A5Product], List[AdaptedA5Product]],
        cortisol_phase: bool = False,
        cortisol_phase_duration: int = CORTISOL_PHASE_DURATION_DAYS,
        adapted: bool = False,
    ):
        if not products:
            raise ValueError("products cannot be None or empty")

        # Convert A5Product → AdaptedA5Product
        if not adapted:
            raw_products = adapter_a5_product(products)
        else:
            raw_products = products

        self.cortisol_phase = cortisol_phase
        self.cortisol_phase_duration = cortisol_phase_duration * cortisol_phase
        # Validate and normalize products
        self.products = self._validate_and_normalize_products(raw_products)

    def _validate_and_normalize_products(self, products: Dict) -> Dict:
        """Validate and normalize product data"""
        normalized = []

        for product in products:
            # Validate required fields
            if "delay" not in product:
                raise ProductValidationError(
                    f"Product '{product['label']}' missing 'delay' field"
                )

            if "servings" not in product:
                raise ProductValidationError(
                    f"Product '{product['label']}' missing or invalid 'servings'"
                )

            if product["servings"] <= 0:
                raise ProductValidationError(
                    f"Product '{product['label']}' has invalid servings : {product['label']}"
                )

            # Validate and extract posology scheme
            posology_scheme = product.get("posology").first()
            if not posology_scheme:
                raise ProductValidationError(
                    f"Product '{product['label']}' has no posology schemes"
                )

            # Validate duration
            if (
                not posology_scheme.duration_value
                or posology_scheme.duration_value <= 0
            ):
                raise ProductValidationError(
                    f"Product '{product['label']}' has invalid duration: {posology_scheme.duration_value}"
                )

            # Validate total daily quantity
            total_daily_quantity = posology_scheme.get_total_daily_quantity()
            if not total_daily_quantity or total_daily_quantity <= 0:
                raise ProductValidationError(
                    f"Product '{product['label']}' has invalid total daily quantity: {total_daily_quantity}"
                )

            total_daily_intakes_per_unit = int(
                product["servings"] / total_daily_quantity
            )

            # Store normalized product with pre-computed values
            normalized.append(
                {
                    "id": product["id"],
                    "label": strip_tags(product["label"]),
                    "delay": self._compute_product_delay(
                        product["phase"], product["delay"]
                    ),
                    "nutrients": product.get("nutrients"),
                    "phase": product["phase"],
                    "posology_scheme": posology_scheme,
                    "servings": product["servings"],
                    "intake": posology_scheme.intakes.first(),
                    "total_daily_quantity": total_daily_quantity,
                    "total_daily_intakes_per_unit": total_daily_intakes_per_unit,
                    "quantity": 2
                    if self._product_second_unit(
                        product["id"], product["phase"], product["delay"], products
                    )
                    else 1,
                }
            )
            normalized.sort(key=lambda p: p["delay"])

        for dict in normalized:
            # quantity = 1
            # if self._product_second_unit(
            #     dict["id"], dict["phase"], dict["delay"], normalized
            # ):
            #     quantity = 2
            dict.update(
                {
                    "pause_duration": self.get_pause_between_product_unit(dict),
                    "posology_end": dict["total_daily_intakes_per_unit"]
                    * dict["quantity"]
                    + dict["delay"]
                    + self.get_pause_between_product_unit(dict),
                }
            )
        return normalized

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

    def get_microbiote_phase_start(self):
        if self.cortisol_phase_duration > 0:
            # If there's a cortisol phase, find min delay among phase 2 products
            return min(
                (p for p in self.products if p["phase"] == 2),
                key=lambda p: p["delay"],
                default=min(self.products, key=lambda p: p["delay"]),
            )["delay"]
        else:
            # No cortisol phase, find min delay among all products
            return min(self.products, key=lambda p: p["delay"])["delay"]

    def get_microbiote_phase_end(self):
        max_product = max(
            self.products,
            key=lambda p: p["posology_end"],
        )
        return max_product["posology_end"]

    def get_total_daily_intakes_per_product_unit(self, product):
        return product["servings"] / product["total_daily_quantity"]

    def get_pause_between_product_unit(self, product: AdaptedA5Product):
        # No pause if there is only one product unit
        if product["quantity"] == 1:
            return 0

        total_daily_intakes = self.get_total_daily_intakes_per_product_unit(product)

        if total_daily_intakes > MAX_DAYS_BETWEEN_PRODUCT_UNIT:
            return 0

        # if product["posology_scheme"].duration_value <= total_daily_intakes:
        #     return 0

        return int(MAX_DAYS_BETWEEN_PRODUCT_UNIT - total_daily_intakes)

    # Not used anymore
    # def get_product_units_per_posology_scheme(self, product: AdaptedA5Product):
    #     return math.ceil(
    #         product["total_daily_quantity"]
    #         * product["posology_scheme"].duration_value
    #         / product["servings"]
    #     )

    def to_dict(self):
        """Return a serializable dictionary representation of products."""
        serializable_products = []

        for product in self.products:
            serializable_product = {
                "id": product["id"],
                "label": product["label"],
                "delay": product["delay"],
                "phase": product["phase"],
                "quantity": product["quantity"],
                "servings": product["servings"],
                "total_daily_quantity": product["total_daily_quantity"],
                "total_daily_intakes_per_unit": product["total_daily_intakes_per_unit"],
                "pause_duration": product["pause_duration"],
            }

            if product.get("nutrients"):
                serializable_product["nutrients"] = product["nutrients"]

            if product.get("posology_scheme"):
                ps = product["posology_scheme"]
                serializable_product["posology_scheme"] = {
                    "duration_value": ps.duration_value,
                    "day_time": ps.day_time,
                }

            if product.get("intake"):
                intake = product["intake"]
                serializable_product["intake"] = {
                    "time_of_day": intake.time_of_day,
                    "time_of_day_label": intake.time_of_day_label,
                    "unit_icon": intake.unit_icon,
                    "unit_label": intake.unit_label,
                }

            serializable_products.append(serializable_product)

        return serializable_products
