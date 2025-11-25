from typing import List, Union, TypedDict
from django.db.models.query import QuerySet
from templates_app.models.posology_scheme import PosologyScheme
from templates_app.models.posology_intake import PosologyIntake


class NutrientDict(TypedDict):
    id: int
    label: str


class AdaptedA5Product(TypedDict):
    nutrients: List[NutrientDict] | None
    delay: int
    phase: int
    posology: Union[QuerySet[PosologyScheme]]


class A5Product(TypedDict):
    nutrients: List[NutrientDict] | None
    label: str
    posology: str | None
    duration: str | None
    delay: int
    phase: int


class NormalizedProduct(TypedDict):
    """Product with computed values ready for calendar rendering"""

    id: int
    label: str
    delay: int  # Computed delay considering phase and cortisol timing
    nutrients: List[NutrientDict] | None
    phase: int  # Product phase (1 or 2)
    posology_scheme: PosologyScheme  # The selected posology scheme
    servings: int  # Total servings in product package
    intake: PosologyIntake  # First intake from the scheme
    total_daily_quantity: int | float  # Total quantity per day
    total_daily_intakes_per_unit: int  # How many days one unit lasts
    quantity: int  # Number of product units needed (1 or 2)
