from templates_app.models.product import Product
from templates_app.models.posology_scheme import PosologyScheme
from templates_app.models.posology_intake import PosologyIntake
from templates_app.models.posology_intake import TimeOfDay
import random

labels = [
    "Labotix CoPlus",
    "Resvératrol",
    "Labotix MB",
    "Magnésium",
    "TonixX Gold",
    "TonixX Plus",
    "L-Tryptophane 500mg",
    "Multi Vitamine B",
    "Omega 3 Epax®",
    "EPP",
    "ADP Biotics",
    "Mucopure 250 (avec Glutamine)",
    "NADH+",
    "Adrenex",
    "Ashwagandha Bio KSM-66",
    "ERGY Calme",
    "Allicin",
    "Labotix Multifibre",
    "Berberine",
    "Tyrosine",
    "Resveratrol",
    "Mo-Zyme",
    "Permea Intest",
    "Alfa Energy",
]


def populate_database():
    for label in labels:
        product = Product.objects.create(label=label, servings=random.randint(30, 120))
        scheme = PosologyScheme.objects.create(
            product=product,
            duration_value=random.randint(40, 60),
            # duration_value=21,
        )
        PosologyIntake.objects.create(
            scheme=scheme,
            quantity=random.randint(1, 4),
            frequency=random.randint(1, 3),
            time_of_day=TimeOfDay.MORNING
            if random.randint(0, 1) == 0
            else TimeOfDay.EVENING,
        )


def create_mock_a5_product(label: str):
    return {
        "label": label,
        # "delay": 0,
        "delay": random.randint(0, 14),
        # "phase": random.randint(1, 2),
        "phase": 1,
    }
