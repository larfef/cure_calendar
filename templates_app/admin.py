from django.contrib import admin

# If you have django-nested-admin installed
# pip install django-nested-admin
try:
    import nested_admin

    USE_NESTED = True
except ImportError:
    USE_NESTED = False

from .models import Product, PosologySchedule, PosologyIntake, PosologyHistory


if USE_NESTED:
    # Nested version - shows intakes within schedules
    class PosologyIntakeInline(nested_admin.NestedTabularInline):
        model = PosologyIntake
        extra = 1
        fields = [
            "order",
            "quantity",
            "unit",
            "time_of_day",
            "specific_time",
            "intake_condition",
            "frequency",
        ]
        ordering = ["order"]

    class PosologyScheduleInline(nested_admin.NestedStackedInline):
        model = PosologySchedule
        extra = 0
        fields = [
            "name",
            "order",
            "duration_value",
            "duration_type",
            "instructions",
            "is_active",
        ]
        inlines = [PosologyIntakeInline]
        ordering = ["order"]

    class ProductAdmin(nested_admin.NestedModelAdmin):
        list_display = ["__str__", "price"]

        inlines = [PosologyScheduleInline]

else:
    # Standard version - click into schedule to see intakes
    class PosologyIntakeInline(admin.TabularInline):
        model = PosologyIntake
        extra = 1
        fields = [
            "order",
            "quantity",
            "unit",
            "time_of_day",
            "specific_time",
            "intake_condition",
            "frequency",
        ]
        ordering = ["order"]

    class PosologyScheduleInline(admin.StackedInline):
        model = PosologySchedule
        extra = 0
        fields = [
            "name",
            "order",
            "duration_value",
            "duration_type",
            "instructions",
            "is_active",
        ]
        ordering = ["order"]

    class ProductAdmin(admin.ModelAdmin):
        list_display = ["__str__", "get_nutrients", "price"]

        def get_nutrients(self, obj):
            nutrients = []
            for nutrient in obj.nutrients.all():
                nutrients.append(nutrient.label)
            return " ,".join(nutrients)

        inlines = [PosologyScheduleInline]


# Register PosologySchedule separately so you can edit intakes when clicking on a schedule
class PosologyScheduleAdmin(admin.ModelAdmin):
    list_display = ["product", "name", "order", "is_active"]
    list_filter = ["is_active", "duration_type"]
    search_fields = ["product__label", "name"]
    inlines = [PosologyIntakeInline]


@admin.register(PosologyIntake)
class PosologyIntakeAdmin(admin.ModelAdmin):
    list_display = [
        "schedule",
        "quantity",
        "unit",
        "time_of_day",
        "intake_condition",
        "frequency",
        "daily_quantity",
    ]
    list_filter = ["unit", "time_of_day", "intake_condition"]
    search_fields = ["schedule__product__label"]

    def daily_quantity(self, obj):
        return obj.get_daily_quantity()

    daily_quantity.short_description = "Quantité/jour"


@admin.register(PosologyHistory)
class PosologyHistoryAdmin(admin.ModelAdmin):
    list_display = ["product", "change_date", "changed_by", "change_description"]
    list_filter = ["change_date"]
    search_fields = ["product__label", "change_description"]
    readonly_fields = ["change_date", "changed_by", "old_values", "new_values"]


# Register the admins
# IMPORTANT: Register Product and PosologySchedule AFTER they are defined above
admin.site.register(Product, ProductAdmin)
admin.site.register(PosologySchedule, PosologyScheduleAdmin)
