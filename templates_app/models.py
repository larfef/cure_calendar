from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator
from tinymce.models import HTMLField


class IntakeUnit(models.TextChoices):
    """Unit types for dosage"""

    CAPSULE = "CAPSULE", "Gélule(s)"
    TABLET = "TABLET", "Comprimé(s)"
    ML = "ML", "ml"
    DROP = "DROP", "Goutte(s)"
    DOSE = "DOSE", "Dose(s)"
    DOSETTE = "DOSETTE", "Dosette(s)"
    SACHET = "SACHET", "Sachet(s)"
    SPRAY = "SPRAY", "Spray(s)"


class TimeOfDay(models.TextChoices):
    """When to take the supplement"""

    MORNING = "MORNING", "Matin"
    NOON = "NOON", "Midi"
    AFTERNOON = "AFTERNOON", "Après-midi"
    EVENING = "EVENING", "Soir"
    BEDTIME = "BEDTIME", "Au coucher"
    ANYTIME = "ANYTIME", "N'importe quand"


class IntakeCondition(models.TextChoices):
    """Special conditions for intake"""

    EMPTY_STOMACH = "EMPTY_STOMACH", "À jeun"
    WITH_MEAL = "WITH_MEAL", "Pendant le repas"
    AFTER_MEAL = "AFTER_MEAL", "Après le repas"
    BEFORE_MEAL = "BEFORE_MEAL", "Avant le repas"
    SPECIFIC_TIME = "SPECIFIC_TIME", "Heure spécifique"
    NO_CONDITION = "NO_CONDITION", "Aucune condition"


class DurationUnit(models.TextChoices):
    """Duration unit types"""

    DAYS = "DAYS", "Jour(s)"
    WEEKS = "WEEKS", "Semaine(s)"
    MONTHS = "MONTHS", "Mois"
    CONTINUOUS = "CONTINUOUS", "En continu"


class Product(models.Model):
    """Updated Product model"""

    label = HTMLField(default=None, blank=True, null=True, verbose_name="Label")

    phase = models.IntegerField(
        default=1, verbose_name="Phase (cortisol=1, microbiote=2)"
    )

    # New field: link to structured posology
    use_structured_posology = models.BooleanField(
        default=False, verbose_name="Utiliser la posologie structurée"
    )

    def __str__(self):
        from bs4 import BeautifulSoup

        nutrient_label = BeautifulSoup(self.label, features="html.parser")
        return str(nutrient_label.get_text())

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
        return sum(intake.quantity * intake.frequency for intake in self.intakes.all())

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


class PosologyIntake(models.Model):
    """
    A single intake within a posology schedule.
    Example: "2 gélules le matin à jeun"
    """

    schedule = models.ForeignKey(
        PosologyScheme,
        on_delete=models.CASCADE,
        related_name="intakes",
        verbose_name="Schéma posologique",
    )

    # Quantity and unit
    quantity = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        verbose_name="Quantité",
        validators=[MinValueValidator(0.1)],
        help_text="Ex: 1, 2, 0.5, 10",
    )

    intake_unit = models.CharField(
        max_length=20,
        choices=IntakeUnit.choices,
        default=IntakeUnit.CAPSULE,
        verbose_name="Unité",
    )

    # Timing
    time_of_day = models.CharField(
        max_length=20, choices=TimeOfDay.choices, verbose_name="Moment de la journée"
    )

    # Conditions
    intake_condition = models.CharField(
        max_length=20,
        choices=IntakeCondition.choices,
        default=IntakeCondition.NO_CONDITION,
        verbose_name="Condition de prise",
    )

    # Frequency (how many times per day)
    frequency = models.PositiveIntegerField(
        default=1,
        verbose_name="Fréquence par jour",
        validators=[MinValueValidator(1)],
        help_text="Nombre de fois par jour",
    )

    # Order within the schedule
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")

    # Additional notes
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        verbose_name = "Prise posologique"
        verbose_name_plural = "Prises posologiques"
        ordering = ["schedule", "time_of_day", "order"]

    def __str__(self):
        text = f"{self.quantity} {self.intake_unit}"
        if self.time_of_day != "ANYTIME":
            text += f" - {self.time_of_day}"
        if self.frequency > 1:
            text += f" (x{self.frequency})"
        return text

    @property
    def unit_icon(self):
        """Return SVG path for the intake unit"""
        UNIT_ICON = {
            IntakeUnit.CAPSULE: "templates_app/images/capsule.svg",
            IntakeUnit.DROP: "templates_app/images/drop.svg",
            IntakeUnit.ML: "templates_app/images/drop.svg",
            IntakeUnit.DOSETTE: "templates_app/images/dosette.svg",
        }

        # Designer make us crazy
        # Exception when icon depends on unit and quantity
        if self.intake_unit == "CAPSULE" and self.quantity > 1:
            return "templates_app/images/capsules.svg"
        return UNIT_ICON.get(self.intake_unit)

    @property
    def time_of_day_icon(self):
        """Return SVG path for the intake time of day"""
        TIME_OF_DAY = {
            TimeOfDay.MORNING: "templates_app/images/morning.svg",
            TimeOfDay.EVENING: "templates_app/images/evening.svg",
        }

        # Exception when icon depends on intake condition instead of time of day
        if self.intake_condition == "EMPTY_STOMACH":
            return "templates_app/images/empty_stomach.svg"
        return TIME_OF_DAY.get(self.time_of_day)

    @property
    def time_of_day_label(self):
        return TimeOfDay(self.time_of_day).label

    def get_intake_condition(self):
        return IntakeCondition(self.intake_condition).label

    @property
    def unit_label(self):
        return IntakeUnit(self.intake_unit).label

    def is_quantity_whole_number(self):
        """
        Check if quantity is a whole number
        Note : Works for first digit after decimal point only
        """
        return not self.quantity * 10 % 10

    @property
    def daily_quantity(self):
        """Calculate quantity per day for this intake"""

        quantity = self.quantity
        if self.is_quantity_whole_number():
            quantity = int(self.quantity)
        if self.frequency > 1:
            return f"{self.frequency} x {quantity}"
        return quantity


# Optional: Track posology changes over time
class PosologyHistory(models.Model):
    """
    Historical record of posology changes for auditing purposes
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="posology_history",
        verbose_name="Produit",
    )

    schedule = models.ForeignKey(
        PosologyScheme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Schéma posologique",
    )

    change_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de modification"
    )

    changed_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Modifié par",
    )

    change_description = models.TextField(verbose_name="Description du changement")

    # Store old values as JSON
    old_values = models.JSONField(
        blank=True, null=True, verbose_name="Anciennes valeurs"
    )

    new_values = models.JSONField(
        blank=True, null=True, verbose_name="Nouvelles valeurs"
    )

    class Meta:
        verbose_name = "Historique posologique"
        verbose_name_plural = "Historiques posologiques"
        ordering = ["-change_date"]

    def __str__(self):
        return f"{self.product} - {self.change_date.strftime('%Y-%m-%d %H:%M')}"
