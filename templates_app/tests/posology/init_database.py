from templates_app.models.product import Product
from templates_app.models.posology_scheme import PosologyScheme
from templates_app.models.posology_intake import PosologyIntake
import random
from typing import Dict, Any


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


def create_mock_product_data(label: str) -> Dict[str, Any]:
    """Create a mock product with scheme and intake data without database"""
    servings = random.randint(30, 120)
    duration_value = random.randint(15, 90)
    quantity = random.randint(1, 4)
    frequency = random.randint(1, 3)

    return {
        "name": label,
        "servings": servings,
        "delay": random.randint(0, 5),  # if random.randint(0, 1) else 0
        "phase": random.randint(1, 2),
        "icon": "pill.svg",
        "scheme": {
            "duration_value": duration_value,
            "duration_unit": "DAYS",
            "order": 1,
            "is_active": True,
            "intake": {
                "quantity": quantity,
                "frequency": frequency,
                "intake_unit": "CAPSULE",
                "time_of_day": "ANYTIME",
                "intake_condition": "NO_CONDITION",
            },
        },
    }


def populate_database():
    for label in labels:
        product = Product.objects.create(label=label, servings=random.randint(30, 120))
        scheme = PosologyScheme.objects.create(
            product=product, duration_value=random.randint(15, 90)
        )
        PosologyIntake.objects.create(
            scheme=scheme, quantity=random.randint(1, 4), frequency=random.randint(1, 3)
        )
