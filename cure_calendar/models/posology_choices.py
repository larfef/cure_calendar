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

    CAPSULE = "CAPSULE", "Gélule"
    TABLET = "TABLET", "Comprimé"
    ML = "ML", "ml"
    DROP = "DROP", "Capuchon"
    DOSE = "DOSE", "Dose"
    DOSETTE = "DOSETTE", "Dosette"
    SACHET = "SACHET", "Sachet"
    SPRAY = "SPRAY", "Spray"


class TimeOfDay(models.TextChoices):
    """When to take the supplement"""

    MORNING = "MORNING", "Matin"
    EVENING = "EVENING", "Soir"
    MIXED = "MIXED", "Matin et soir"
    ANYTIME = "ANYTIME", "N'importe quand"
