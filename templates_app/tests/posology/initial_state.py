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
            # duration_value=random.randint(15, 30)
            duration_value=25,
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
        "delay": random.randint(0, 7),
        # "phase": random.randint(1, 2),
        "phase": 1,
    }


# def create_mock_product_data(label: str) -> Dict[str, Any]:
#     """Create a mock product with scheme and intake data without database"""

#     return {
#         "label": label,
#         "servings": random.randint(30, 120),
#         "delay": random.randint(0, 5),  # if random.randint(0, 1) else 0
#         "phase": random.randint(1, 2),
#         "icon": "pill.svg",
#         "posology": {
#             "duration_value": random.randint(15, 90),
#             "duration_unit": "DAYS",
#             "order": 1,
#             "is_active": True,
#             "intake": {
#                 "quantity": random.randint(1, 4),
#                 "frequency": random.randint(1, 3),
#                 "intake_unit": "CAPSULE",
#                 "time_of_day": "ANYTIME",
#                 "intake_condition": "NO_CONDITION",
#             },
#         },
#     }
