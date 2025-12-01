from typing import Callable
from django.db import models
from tinymce.models import HTMLField
from cure_calendar.models.posology_choices import IntakeUnit


class Product(models.Model):
    """Updated Product model"""

    # === Existing fields ===
    label = HTMLField(default=None, blank=True, null=True, verbose_name="Label")
    phase = models.PositiveIntegerField(default=1, null=True, blank=True)
    shopify_id = models.BigIntegerField(
        default=None, blank=True, null=True, verbose_name="Shopify Product ID"
    )
    # === New fields ===
    servings = models.PositiveIntegerField(
        default=50, verbose_name="Nombre total de dose par produit"
    )
    serving_unit = models.CharField(
        max_length=30,
        choices=IntakeUnit.choices,
        default=IntakeUnit.CAPSULE,
        verbose_name="Unité de dosage",
    )
    use_structured_posology = models.BooleanField(
        default=False, verbose_name="Utiliser la posologie structurée"
    )

    # === Methods ===

    def _has_second_unit(self, rule: Callable[[int], bool]) -> bool:
        return rule(self.id)

    def _has_exception(self, rule: Callable[[int], bool]) -> bool:
        return rule(self.id)

    def get_posology_display(self):
        """Generate human-readable posology from structured data"""
        if self.use_structured_posology and self.posology_schemes.exists():
            return self._format_structured_posology()
        return self.posology_legacy

    def _format_structured_posology(self):
        """Format structured posology as list"""
        schemes = self.posology_schemes.all().order_by("order")
        lines = []
        for scheme in schemes:
            intakes = scheme.intakes.all().order_by("time_of_day")
            for intake in intakes:
                line = f"{intake.quantity} {intake.get_intake_unit()}"
                if intake.time_of_day != "ANYTIME":
                    line += f" {intake.get_time_of_day()}"
                if intake.intake_condition != "NO_CONDITION":
                    line += f" ({intake.get_intake_condition()})"
                lines.append(line)
        return "".join(lines)

    class Meta:
        verbose_name_plural = "Produits"
