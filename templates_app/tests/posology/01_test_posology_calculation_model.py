from django.test import TestCase
from templates_app.classes.posology_calculation_model import PosologyCalculationModel
from templates_app.logging.log_database_state_to_yaml import (
    log_database_state_to_yaml,
)
from templates_app.tests.posology.initial_state import (
    populate_database,
    create_mock_a5_product,
    labels,
)
import random

# === Dummy import to get Product methods with debugpy
from templates_app.models.product import Product


class TestPosolgyCalculationModel(TestCase):
    def setUp(self):
        populate_database()
        log_database_state_to_yaml()

        self.a5_products = [
            create_mock_a5_product(labels[v])
            for v in random.sample(
                range(0, len(labels)), random.randint(4, len(labels))
            )
        ]

        self.calculator = PosologyCalculationModel(
            self.a5_products, cortisol_phase=True
        )

        pass

    def test_methods(self):
        pass
