from django.db import models


class DurationUnit(models.TextChoices):
    """Duration unit types"""

    DAYS = "DAYS", "Jour(s)"
    WEEKS = "WEEKS", "Semaine(s)"
    MONTHS = "MONTHS", "Mois"
    CONTINUOUS = "CONTINUOUS", "En continu"


class IntakeCondition(models.TextChoices):
    """Special conditions for intake"""

    AFTER_MEAL = "AFTER_MEAL", "Après le repas"
    NO_CONDITION = "NO_CONDITION", "Aucune condition"


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
    EVENING = "EVENING", "Soir"
    ANYTIME = "ANYTIME", "N'importe quand"
