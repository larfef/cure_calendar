from typing import List, Union, TypedDict
from django.db.models.query import QuerySet
from templates_app.models.posology_scheme import PosologyScheme


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
