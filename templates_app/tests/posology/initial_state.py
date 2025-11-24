from templates_app.models.product import Product
from templates_app.models.posology_scheme import PosologyScheme
from templates_app.models.posology_intake import PosologyIntake
from templates_app.models.posology_intake import IntakeUnit, TimeOfDay
import random

labels = [
    ("Labotix CoPlus", 1),
    ("Resvératrol", 2),
    ("Labotix MB", 3),
    ("Magnésium", 4),
    ("L-Tryptophane 500mg", 7),
    ("Multi Vitamine B", 8),
    ("Omega 3 Epax®", 9),
    ("EPP", 10),
    ("ADP Biotics", 11),
    ("Mucopure 250 (avec Glutamine)", 13),
    ("NADH+", 14),
    ("Adrenex", 15),
    ("Ashwagandha Bio KSM-66", 16),
    ("ERGY Calme", 17),
    ("Allicin", 18),
    ("Labotix Multifibre", 19),
    ("Berberine", 20),
    ("Resveratrol", 23),
    ("Mo-Zyme", 24),
    ("Permea Intest", 25),
    ("Alfa Energy", 26),
]

intake_units = [
    "CAPSULE",
    "DROP",
    "DOSETTE",
    # "TABLET",
    # "ML",
    # "SPRAY"
]

time_of_day = ["MORNING", "EVENING", "MIXED"]


def populate_database():
    for label in labels:
        product = Product.objects.create(
            id=label[1],
            label=label[0],
            servings=30,
            # servings=random.randint(30, 120)
        )
        scheme = PosologyScheme.objects.create(
            product=product,
            duration_value=random.randint(40, 60),
            # duration_value=21,
        )

        PosologyIntake.objects.create(
            scheme=scheme,
            quantity=random.randint(1, 4),
            frequency=random.randint(1, 3),
            time_of_day=time_of_day[random.randint(0, 2)],
            intake_unit=intake_units[random.randint(0, 2)],
        )


def create_mock_a5_product(label: str):
    return {
        "label": label,
        # "delay": 6,
        "delay": random.randint(0, 14),
        "phase": random.randint(1, 2),
        # "phase": 1,
    }
