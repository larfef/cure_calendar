import random
from templates_app.models.product import Product
from templates_app.models.posology_scheme import PosologyScheme
from templates_app.models.posology_intake import PosologyIntake
from templates_app.models.posology_intake import IntakeUnit, TimeOfDay
from pathlib import Path
import yaml
from typing import List, Dict

# Label, Id, Servings, Duration Value, Quantity, Frequency

MOCK_PRODUCTS = {
    "Labotix CoPlus": {
        "id": 1,
        "servings": 120,
        "duration": 60,
        "quantity": 3,
        "frequency": 1,
        "time_of_day": "MIXED",
        "intake_unit": "CAPSULE",
    },
    "Resveratrol": {
        "id": 2,
        "servings": 60,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "MIXED",
        "intake_unit": "CAPSULE",
    },
    "Labotix MB": {
        "id": 3,
        "servings": 30,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "DROP",
    },
    "Magnésium bisglycinate": {
        "id": 4,
        "servings": 180,
        "duration": 60,
        "quantity": 3,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "CAPSULE",
    },
    "Tryptophane": {
        "id": 7,
        "servings": 60,
        "duration": 60,
        "quantity": 2,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "CAPSULE",
    },
    "Vitamine B Complex": {
        "id": 8,
        "servings": 60,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "MORNING",
        "intake_unit": "CAPSULE",
    },
    "Omega 3 Epax®": {
        "id": 9,
        "servings": 90,
        "duration": 60,
        "quantity": 2,
        "frequency": 1,
        "time_of_day": "MIXED",
        "intake_unit": "DOSETTE",
    },
    "EPP": {
        "id": 10,
        "servings": 60,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "MORNING",
        "intake_unit": "DROP",
    },
    "ADP Biotics": {
        "id": 11,
        "servings": 60,
        "duration": 60,
        "quantity": 4,
        "frequency": 1,
        "time_of_day": "MIXED",
        "intake_unit": "CAPSULE",
    },
    "Mucopure": {
        "id": 13,
        "servings": 17,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "MORNING",
        "intake_unit": "DOSETTE",
    },
    "Adrenex": {
        "id": 15,
        "servings": 60,
        "duration": 60,
        "quantity": 2,
        "frequency": 1,
        "time_of_day": "MORNING",
        "intake_unit": "CAPSULE",
    },
    "Ashwagandha Bio KSM-66": {
        "id": 16,
        "servings": 60,
        "duration": 60,
        "quantity": 2,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "CAPSULE",
    },
    "ERGY CALM": {
        "id": 17,
        "servings": 25,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "DOSETTE",
    },
    "Allicine": {
        "id": 18,
        "servings": 90,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "MORNING",
        "intake_unit": "CAPSULE",
    },
    "Labotix Multifibre": {
        "id": 19,
        "servings": 19,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "DOSETTE",
    },
    "Berbérine": {
        "id": 20,
        "servings": 60,
        "duration": 60,
        "quantity": 2,
        "frequency": 1,
        "time_of_day": "MIXED",
        "intake_unit": "CAPSULE",
    },
    "Mo-Zyme": {
        "id": 24,
        "servings": 100,
        "duration": 60,
        "quantity": 3,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "CAPSULE",
    },
    "Alfa Permea Intest": {
        "id": 25,
        "servings": 21,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "MORNING",
        "intake_unit": "DOSETTE",
    },
    "Alfa Energy": {
        "id": 26,
        "servings": 60,
        "duration": 60,
        "quantity": 2,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "DROP",
    },
}

intake_units = [
    "CAPSULE",
    "DROP",
    "DOSETTE",
]

time_of_day = ["MORNING", "EVENING", "MIXED"]


def populate_database():
    # for label in labels:
    #     product = Product.objects.create(
    #         id=label[1],
    #         label=label[0],
    #         # servings=21,
    #         servings=random.randint(20, 40),
    #     )
    #     scheme = PosologyScheme.objects.create(
    #         product=product,
    #         duration_value=random.randint(20, 40),
    #         # duration_value=30,
    #     )

    #     PosologyIntake.objects.create(
    #         scheme=scheme,
    #         # quantity=random.randint(1, 4),
    #         # frequency=random.randint(1, 3),
    #         quantity=1,
    #         frequency=1,
    #         time_of_day=time_of_day[random.randint(0, 2)],
    #         intake_unit=intake_units[random.randint(0, 2)],
    #     )
    for label, data in MOCK_PRODUCTS.items():
        product_db = Product.objects.create(
            label=label,
            phase=random.randint(1, 2),
            id=data["id"],
            servings=data["servings"],
        )
        scheme = PosologyScheme.objects.create(
            product=product_db,
            duration_value=data["duration"],
        )
        PosologyIntake.objects.create(
            scheme=scheme,
            quantity=data["quantity"],
            frequency=data["frequency"],
            time_of_day=data["time_of_day"],
            intake_unit=data["intake_unit"],
        )


def load_products_from_yaml(yaml_path: str = "products_snapshot.yaml") -> List[Dict]:
    """
    Load products from YAML file and convert back to A5Product format.

    Returns a list of A5Products with label, delay, and phase fields
    that can be passed to PosologyCalculationModel.
    """
    yaml_file = Path(yaml_path)

    if not yaml_file.exists():
        raise FileNotFoundError(f"YAML file not found: {yaml_path}")

    with yaml_file.open("r", encoding="utf-8") as f:
        products_data = yaml.safe_load(f)

    # Convert back to A5Product format (minimal fields needed)
    a5_products = []
    for product in products_data:
        a5_products.append(
            {
                "label": product["label"],
                "delay": product["base_delay"],
                "phase": product["phase"],
            }
        )

    return a5_products
