from django.contrib import admin

# If you have django-nested-admin installed
# pip install django-nested-admin
try:
    import nested_admin

    USE_NESTED = True
except ImportError:
    USE_NESTED = False

from cure_calendar.models.posology_intake import PosologyIntake
from cure_calendar.models.posology_scheme import PosologyScheme
from cure_calendar.models.product import Product

if USE_NESTED:
    # Nested version - shows intakes within schedules
    class PosologyIntakeInline(nested_admin.NestedTabularInline):
        model = PosologyIntake
        extra = 1
        fields = [
            "order",
            "quantity",
            "intake_unit",
            "time_of_day",
            "intake_condition",
            "frequency",
        ]
        ordering = ["order"]

    class PosologySchemeInline(nested_admin.NestedStackedInline):
        model = PosologyScheme
        extra = 0
        fields = [
            "name",
            "order",
            "duration_value",
            "duration_unit",
            "instructions",
            "is_active",
        ]
        inlines = [PosologyIntakeInline]
        ordering = ["order"]

    class ProductAdmin(nested_admin.NestedModelAdmin):
        list_display = ["__str__"]

        inlines = [PosologySchemeInline]

else:
    # Standard version - click into schedule to see intakes
    class PosologyIntakeInline(admin.TabularInline):
        model = PosologyIntake
        extra = 1
        fields = [
            "order",
            "quantity",
            "intake_unit",
            "time_of_day",
            "intake_condition",
            "frequency",
        ]
        ordering = ["order"]

    class PosologySchemeInline(admin.StackedInline):
        model = PosologyScheme
        extra = 0
        fields = [
            "name",
            "order",
            "duration_value",
            "duration_unit",
            "instructions",
            "is_active",
        ]
        ordering = ["order"]

    class ProductAdmin(admin.ModelAdmin):
        list_display = ["__str__", "get_nutrients"]

        def get_nutrients(self, obj):
            nutrients = []
            for nutrient in obj.nutrients.all():
                nutrients.append(nutrient.label)
            return " ,".join(nutrients)

        inlines = [PosologySchemeInline]


# Register PosologySchedule separately so you can edit intakes when clicking on a schedule
class PosologyScheduleAdmin(admin.ModelAdmin):
    list_display = ["product", "name", "order", "is_active"]
    list_filter = ["is_active", "duration_unit"]
    search_fields = ["product__label", "name"]
    inlines = [PosologyIntakeInline]


@admin.register(PosologyIntake)
class PosologyIntakeAdmin(admin.ModelAdmin):
    list_display = [
        "scheme",
        "quantity",
        "intake_unit",
        "time_of_day",
        "intake_condition",
        "frequency",
        "daily_quantity",
    ]
    list_filter = ["intake_unit", "time_of_day", "intake_condition"]
    search_fields = ["scheme__product__label"]

    def daily_quantity(self, obj):
        return obj.get_daily_quantity()

    daily_quantity.short_description = "Quantité/jour"


# Register the admins
# IMPORTANT: Register Product and PosologySchedule AFTER they are defined above
admin.site.register(Product, ProductAdmin)
admin.site.register(PosologyScheme, PosologyScheduleAdmin)
