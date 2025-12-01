import random
from templates_app.models.product import Product
from templates_app.models.posology_scheme import PosologyScheme
from templates_app.models.posology_intake import PosologyIntake
from pathlib import Path
import yaml

from templates_app.types import ProductsData

# Label, Id, Servings, Duration Value, Quantity, Frequency

MOCK_PRODUCTS = {
    "Labotix CoPlus": {
        "id": 1,
        "shopify_id": "9848954126665",
        "servings": 120,
        "duration": 60,
        "quantity": 3,
        "frequency": 1,
        "time_of_day": "MIXED",
        "intake_unit": "CAPSULE",
        "phase": 2,  # Changed from 1 to 2
    },
    "Resveratrol": {
        "id": 2,
        "shopify_id": "9845273133385",
        "servings": 60,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "MIXED",
        "intake_unit": "CAPSULE",
        "phase": 2,  # Already 2
    },
    "Labotix MB": {
        "id": 3,
        "shopify_id": "9845272445257",
        "servings": 30,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "DROP",
        "phase": 2,  # Changed from 1 to 2
    },
    "Magnésium bisglycinate": {
        "id": 4,
        "shopify_id": "9845272510793",
        "servings": 180,
        "duration": 60,
        "quantity": 3,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "CAPSULE",
        "phase": 1,  # Changed from 2 to 1
    },
    "Tryptophane": {
        "id": 7,
        "shopify_id": "9845272609097",
        "servings": 60,
        "duration": 60,
        "quantity": 2,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "CAPSULE",
        "phase": 1,  # Already 1
    },
    "Vitamine B Complex": {
        "id": 8,
        "shopify_id": "9850479051081",
        "servings": 60,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "MORNING",
        "intake_unit": "CAPSULE",
        "phase": 1,  # Changed from 2 to 1
    },
    "Omega 3 Epax®": {
        "id": 9,
        "shopify_id": "9845272674633",
        "servings": 90,
        "duration": 60,
        "quantity": 2,
        "frequency": 1,
        "time_of_day": "MIXED",
        "intake_unit": "DOSETTE",
        "phase": 2,  # Changed from 1 to 2
    },
    "EPP": {
        "id": 10,
        "shopify_id": "9845272707401",
        "servings": 60,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "MORNING",
        "intake_unit": "DROP",
        "phase": 2,  # Already 2
    },
    "ADP Biotics": {
        "id": 11,
        "shopify_id": "9845272740169",
        "servings": 60,
        "duration": 60,
        "quantity": 4,
        "frequency": 1,
        "time_of_day": "MIXED",
        "intake_unit": "CAPSULE",
        "phase": 2,  # Changed from 1 to 2
    },
    "Mucopure": {
        "id": 13,
        "shopify_id": "9845272805705",
        "servings": 17,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "MORNING",
        "intake_unit": "DOSETTE",
        "phase": 1,  # Changed from 2 to 1
    },
    "Adrenex": {
        "id": 15,
        "shopify_id": "9845272871241",
        "servings": 60,
        "duration": 60,
        "quantity": 2,
        "frequency": 1,
        "time_of_day": "MORNING",
        "intake_unit": "CAPSULE",
        "phase": 1,  # Already 1
    },
    "Ashwagandha Bio KSM-66": {
        "id": 16,
        "shopify_id": "9845272904009",
        "servings": 60,
        "duration": 60,
        "quantity": 2,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "CAPSULE",
        "phase": 1,  # Changed from 2 to 1
    },
    "ERGY CALM": {
        "id": 17,
        "shopify_id": "9845272936777",
        "servings": 25,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "DOSETTE",
        "phase": 1,  # Already 1
    },
    "Allicine": {
        "id": 18,
        "shopify_id": "9845272969545",
        "servings": 90,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "MORNING",
        "intake_unit": "CAPSULE",
        "phase": 2,  # Already 2
    },
    "Labotix Multifibre": {
        "id": 19,
        "shopify_id": "9845273002313",
        "servings": 19,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "DOSETTE",
        "phase": 2,  # Changed from 1 to 2
    },
    "Berbérine": {
        "id": 20,
        "shopify_id": "9845273035081",
        "servings": 60,
        "duration": 60,
        "quantity": 2,
        "frequency": 1,
        "time_of_day": "MIXED",
        "intake_unit": "CAPSULE",
        "phase": 2,  # Already 2
    },
    "Mo-Zyme": {
        "id": 24,
        "shopify_id": "9845273166153",
        "servings": 100,
        "duration": 60,
        "quantity": 3,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "CAPSULE",
        "phase": 2,  # Changed from 1 to 2
    },
    "Alfa Permea Intest": {
        "id": 25,
        "shopify_id": "9845273198921",
        "servings": 21,
        "duration": 60,
        "quantity": 1,
        "frequency": 1,
        "time_of_day": "MORNING",
        "intake_unit": "DOSETTE",
        "phase": 2,  # Already 2
    },
    "Alfa Energy": {
        "id": 26,
        "shopify_id": "9850458276169",
        "servings": 60,
        "duration": 60,
        "quantity": 2,
        "frequency": 1,
        "time_of_day": "EVENING",
        "intake_unit": "DROP",
        "phase": 1,  # Already 1
    },
}

intake_units = [
    "CAPSULE",
    "DROP",
    "DOSETTE",
]

time_of_day = ["MORNING", "EVENING", "MIXED"]


def populate_database():
    for label, data in MOCK_PRODUCTS.items():
        product_db = Product.objects.create(
            label=label,
            phase=data["phase"],
            id=data["id"],
            shopify_id=data["shopify_id"],
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


def load_products_from_yaml(yaml_path: str = "products_snapshot.yaml") -> ProductsData:
    """
    Load products from YAML file and reconstruct ProductsData structure.

    Returns ProductsData TypedDict with:
        - products: Dict[int, Product] - Django Product instances fetched from DB
        - delays: Dict[int, int] - Delay for each product
        - cortisol_phase: bool - Whether cortisol phase is active
    """
    from templates_app.models.product import Product

    yaml_file = Path(yaml_path)

    if not yaml_file.exists():
        raise FileNotFoundError(f"YAML file not found: {yaml_path}")

    with yaml_file.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Reconstruct ProductsData structure
    products_data: ProductsData = {
        "products": {},
        "delays": data["delays"],
        "cortisol_phase": data["cortisol_phase"],
    }

    # Fetch Product instances from database
    for product_id in data["product_ids"]:
        products_data["products"][product_id] = Product.objects.get(id=product_id)

    return products_data
