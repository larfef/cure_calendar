import math
from typing import Dict, List, Union
from templates_app.models.product import Product
from templates_app.types.product import A5Product, AdaptedA5Product


CORTISOL_PHASE_DURATION_DAYS = 28
MAX_DAYS_BETWEEN_PRODUCT_UNIT = 30


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

    new_products: Dict[AdaptedA5Product] = {}
    for product in products:
        adapted_product = product_lookup.get(product["label"])

        if adapted_product:
            new_products.update(
                {
                    product["label"]: {
                        "nutrients": product.get("nutrients"),
                        "posology": adapted_product.posology_schemes.all(),  # QuerySet
                        "servings": adapted_product.servings,
                        "delay": product["delay"],
                        "phase": product["phase"],
                    }
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

        # Validate and normalize all products upfront
        self.products = self._validate_and_normalize_products(raw_products)
        self.cortisol_phase_duration = cortisol_phase_duration

    def _validate_and_normalize_products(self, products: Dict) -> Dict:
        """Validate and normalize product data"""
        normalized = {}

        for label, product in products.items():
            # Validate required fields
            if "delay" not in product:
                raise ProductValidationError(f"Product '{label}' missing 'delay' field")

            if "servings" not in product:
                raise ProductValidationError(
                    f"Product '{label}' missing or invalid 'servings'"
                )

            if product["servings"] <= 0:
                raise ProductValidationError(
                    f"Product '{label}' has invalid servings : {product['servings']}"
                )

            # Validate and extract posology scheme
            posology_qs = product.get("posology")
            if not posology_qs or not posology_qs.exists():
                raise ProductValidationError(
                    f"Product '{label}' has no posology schemes"
                )

            posology_scheme = posology_qs.first()

            # Validate duration
            if (
                not posology_scheme.duration_value
                or posology_scheme.duration_value <= 0
            ):
                raise ProductValidationError(
                    f"Product '{label}' has invalid duration: {posology_scheme.duration_value}"
                )

            # Validate total daily quantity
            total_daily_quantity = posology_scheme.get_total_daily_quantity()
            if not total_daily_quantity or total_daily_quantity <= 0:
                raise ProductValidationError(
                    f"Product '{label}' has invalid total daily quantity: {total_daily_quantity}"
                )

            total_daily_intakes_per_unit = product["servings"] / total_daily_quantity

            # Store normalized product with pre-computed values
            normalized[label] = {
                "delay": product["delay"],
                "nutrients": product.get("nutrients"),
                "phase": product.get("phase"),
                "posology_scheme": posology_scheme,
                "servings": product["servings"],
                "total_daily_quantity": total_daily_quantity,
                "total_daily_intakes_per_unit": total_daily_intakes_per_unit,
            }

        return normalized

    def get_microbiote_phase_start(self):
        return (
            self.cortisol_phase_duration
            + min(self.products.values(), key=lambda p: p["delay"])["delay"]
        )

    def get_microbiote_phase_end(self):
        max_product = max(
            self.products.values(),
            key=lambda p: p["delay"] + p["posology_scheme"].duration_value,
        )
        return (
            self.cortisol_phase_duration
            + max_product["delay"]
            + max_product["posology_scheme"].duration_value
        )

    def get_total_daily_intakes_per_product_unit(self, product):
        return product["servings"] / product["total_daily_quantity"]

    def get_pause_between_product_unit(self, product: AdaptedA5Product):
        total_daily_intakes = self.get_total_daily_intakes_per_product_unit(product)

        if total_daily_intakes > MAX_DAYS_BETWEEN_PRODUCT_UNIT:
            return 0

        if product["posology_scheme"].duration_value <= total_daily_intakes:
            return 0

        return MAX_DAYS_BETWEEN_PRODUCT_UNIT - total_daily_intakes

    def get_product_units_per_posology_scheme(self, product: AdaptedA5Product):
        return math.ceil(
            product["total_daily_quantity"]
            * product["posology_scheme"].duration_value
            / product["servings"]
        )


# class PosologyCalculationModel:
#     def __init__(
#         self,
#         products: Union[List[A5Product], List[AdaptedA5Product]],
#         cortisol_phase_duration: int = CORTISOL_PHASE_DURATION_DAYS,
#         adapted: bool = False,
#     ):
#         if not products:
#             raise ValueError("products cannot be None or empty")

#         # Convert A5Product → AdaptedA5Product
#         if not adapted:
#             self.products = adapter_a5_product(products)
#         else:
#             self.products = products

#         self.cortisol_phase_duration = cortisol_phase_duration

#     def get_microbiote_phase_start(self):
#         return (
#             self.cortisol_phase_duration
#             + min(self.products.values(), key=lambda p: p["delay"])["delay"]
#         )

#     def get_microbiote_phase_end(self):
#         max_product = max(
#             self.products.values(),
#             key=lambda p: p["delay"] + p["posology"].first().duration_value,
#         )
#         return (
#             self.cortisol_phase_duration
#             + max_product["delay"]
#             + max_product["posology"].first().duration_value
#         )

#     def get_product_from_label(self, product_label):
#         product = self.products.get(product_label)
#         return product

#     def get_total_daily_intakes_per_product_unit(self, product):
#         posology = product.get("posology")
#         posology_scheme = posology.first()

#         if not posology_scheme:
#             return None

#         total_daily_quantity = posology_scheme.get_total_daily_quantity()

#         if not total_daily_quantity:
#             return None

#         return product.get("servings", 0) / total_daily_quantity

#     def get_pause_between_product_unit(self, product: AdaptedA5Product):
#         total_daily_intakes = self.get_total_daily_intakes_per_product_unit(product)
#         posology = product.get("posology")

#         if total_daily_intakes > MAX_DAYS_BETWEEN_PRODUCT_UNIT:
#             return 0

#         posology_scheme = posology.first()
#         if posology_scheme and posology_scheme.duration_value <= total_daily_intakes:
#             return 0

#         return MAX_DAYS_BETWEEN_PRODUCT_UNIT - total_daily_intakes

#     def get_product_units_per_posology_scheme(self, product: AdaptedA5Product):
#         posology = product.get("posology")
#         posology_scheme = posology.first()

#         if not posology_scheme:
#             return 0

#         total_daily_quantity = posology_scheme.get_total_daily_quantity()

#         return math.ceil(
#             total_daily_quantity
#             * posology_scheme.duration_value
#             / product.get("servings")
#         )
