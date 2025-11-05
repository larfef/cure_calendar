from django.test import TestCase
from templates_app.classes.posology_calculation_model import PosologyCalculationModel
from templates_app.logging.log_randomized_sample_to_yaml import (
    log_randomized_sample_to_yaml,
)
from templates_app.tests.posology.init_database import (
    log_database_state_to_yaml,
    populate_database,
    get_randomized_products_sample,
)

# === Dummy import to get Product methods with debugpy
from templates_app.models.product import Product


class TestPosolgyCalculationModel(TestCase):
    def setUp(self):
        populate_database()
        log_database_state_to_yaml()

        self.a5_products = get_randomized_products_sample()
        log_randomized_sample_to_yaml(self.a5_products)

        self.calculator = PosologyCalculationModel(self.a5_products)
        pass

    def test_methods(self):
        microbiote_phase_start = self.calculator.get_microbiote_phase_start()
        microbiote_phase_end = self.calculator.get_microbiote_phase_end()

        pass
