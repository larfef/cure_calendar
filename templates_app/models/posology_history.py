from django.db import models
from templates_app.models.posology_scheme import PosologyScheme
from templates_app.models.product import Product


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
