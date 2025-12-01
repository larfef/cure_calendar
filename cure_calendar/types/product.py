from typing import Dict, List, Union, TypedDict
from django.db.models.query import QuerySet
from cure_calendar.models.posology_scheme import PosologyScheme
from cure_calendar.models.posology_intake import PosologyIntake
from cure_calendar.models.product import Product


class NutrientDict(TypedDict):
    id: int
    label: str


class AdaptedA5Product(TypedDict):
    nutrients: List[NutrientDict] | None
    delay: int
    phase: int
    posology: Union[QuerySet[PosologyScheme]]


class ProductsData(TypedDict):
    products: Dict[int, Product]
    delays: Dict[int, int]
    cortisol_phase: bool


class NormalizedProduct(TypedDict):
    """Product with computed values ready for calendar rendering"""

    id: int
    shopify_id: int
    label: str
    phase: int
    posology: PosologyScheme
    base_delay: int
    servings: int
    intake: PosologyIntake
    total_daily_quantity: int | float
    total_daily_intakes_per_unit: int
    first_unit_start: int
    first_unit_end: int
    second_unit: bool  # Whether there is a second unit in the protocol
    second_unit_start: int
    pause_between_unit: int
    posology_end: int
