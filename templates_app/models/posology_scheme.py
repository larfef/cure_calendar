from django.db import models
from templates_app.models.product import Product
from django.core.validators import MinValueValidator
from templates_app.models.posology_choices import DurationUnit


class PosologyScheme(models.Model):
    """
    A posology scheme defines a complete intake pattern for a product.
    A product can have multiple schemes (e.g., different phases of treatment).
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="posology_schemes",
        verbose_name="Produit",
    )

    # Schedule metadata
    name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nom du schéma",
        help_text="Ex: 'Phase d'attaque', 'Phase d'entretien'",
    )

    order = models.PositiveIntegerField(
        default=1, verbose_name="Ordre", help_text="Ordre d'affichage des schémas"
    )

    # Duration of this schedule
    duration_value = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Durée", validators=[MinValueValidator(1)]
    )

    duration_unit = models.CharField(
        max_length=20,
        choices=DurationUnit.choices,
        default=DurationUnit.DAYS,
        verbose_name="Unité de durée",
    )

    # Special instructions
    instructions = models.TextField(
        blank=True,
        null=True,
        verbose_name="Instructions spéciales",
        help_text="Ex: 'Commencer par 1/2 pendant 15 jours'",
    )

    # Is this schedule active?
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Schéma posologique"
        verbose_name_plural = "Schémas posologiques"
        ordering = ["product", "order"]
        unique_together = ["product", "order"]

    def __str__(self):
        name = self.name or f"Schéma {self.order}"
        return f"{self.product} - {name}"

    def get_total_daily_quantity(self):
        """Calculate total daily quantity"""
        return sum(intake.daily_quantity for intake in self.intakes.all())

    @property
    def duration(self):
        return f"{self.duration_value} {DurationUnit(self.duration_unit).label}"

    def get_formatted_intake_quantity_unit(self):
        """
        Returns a list of formatted strings, one for each intake item's quantity and unit.
        """
        return [
            f"{intake.quantity} {intake.get_intake_unit()}"
            for intake in self.intakes.all()
        ]
