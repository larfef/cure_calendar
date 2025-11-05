from templates_app.models.product import Product
from templates_app.models.posology_scheme import PosologyScheme
from templates_app.models.posology_intake import PosologyIntake
import random
from typing import List
from templates_app.types.product import A5Product

# Import logging functions
from templates_app.logging.log_database_state_to_json import log_database_state_to_json
from templates_app.logging.log_database_state_to_yaml import log_database_state_to_yaml
from templates_app.logging.log_database_state_to_csv import log_database_state_to_csv
from templates_app.logging.log_database_state_to_sql import log_database_state_to_sql
from templates_app.logging.log_randomized_sample_to_yaml import (
    log_randomized_sample_to_yaml as _log_randomized_sample_to_yaml,
)

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
            product=product, duration_value=random.randint(15, 90)
        )
        PosologyIntake.objects.create(
            scheme=scheme, quantity=random.randint(1, 4), frequency=random.randint(1, 3)
        )


def get_randomized_products_sample():
    sample = random.sample(range(0, len(labels)), random.randint(4, len(labels)))

    products = []

    for v in sample:
        delay = random.randint(3, 15)  # if random.randint(0, 1) else 0
        products.append(
            {"label": labels[v], "delay": delay, "phase": random.randint(1, 2)}
        )

    return products


def log_randomized_sample_to_yaml(output_file="randomized_sample.yaml"):
    """
    Log the randomized products sample returned by get_randomized_products_sample()
    to a separate YAML file.
    """
    sample = get_randomized_products_sample()
    return _log_randomized_sample_to_yaml(sample, labels, output_file)
