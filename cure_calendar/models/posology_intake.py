from django.db import models
from django.core.validators import MinValueValidator
from cure_calendar.models.posology_scheme import PosologyScheme
from cure_calendar.models.posology_choices import IntakeCondition, IntakeUnit, TimeOfDay


class PosologyIntake(models.Model):
    """
    A single intake within a posology scheme.
    Example: "2 gélules le matin à jeun"
    """

    scheme = models.ForeignKey(
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
        max_length=20,
        default=TimeOfDay.ANYTIME,
        choices=TimeOfDay.choices,
        verbose_name="Moment de la journée",
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
        ordering = ["scheme", "time_of_day", "order"]

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
            IntakeUnit.CAPSULE: "cure_calendar/images/capsules.svg",
            IntakeUnit.DROP: "cure_calendar/images/drop.svg",
            IntakeUnit.ML: "cure_calendar/images/drop.svg",
            IntakeUnit.DOSETTE: "cure_calendar/images/dosette.svg",
        }

        # Designer make us crazy
        # Exception when icon depends on unit and quantity
        if self.intake_unit == "CAPSULE" and self.quantity > 1:
            return "cure_calendar/images/capsules.svg"
        return UNIT_ICON.get(self.intake_unit)

    @property
    def time_of_day_color(self):
        TIME_OF_DAY = {
            TimeOfDay.MORNING: "var(--primary-yellow, #FEFDF3)",
            TimeOfDay.EVENING: "var(--primary-blue, #EFFAFF)",
            TimeOfDay.MIXED: "var(--secondary-green, #EFFFF4)",
        }
        return TIME_OF_DAY.get(self.time_of_day)

    @property
    def time_of_day_icon(self):
        """Return SVG path for the intake time of day"""
        TIME_OF_DAY = {
            TimeOfDay.MORNING: "cure_calendar/images/morning.svg",
            TimeOfDay.EVENING: "cure_calendar/images/evening.svg",
            TimeOfDay.MIXED: "cure_calendar/images/morning_evening.svg",
        }
        return TIME_OF_DAY.get(self.time_of_day)

    @property
    def time_of_day_icon_class(self):
        TIME_OF_DAY = {
            TimeOfDay.MORNING: "legend__icon-svg--morning",
            TimeOfDay.EVENING: "legend__icon-svg--evening",
            TimeOfDay.MIXED: "legend__icon-svg--mixed",
        }
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
        return self.frequency * self.quantity
