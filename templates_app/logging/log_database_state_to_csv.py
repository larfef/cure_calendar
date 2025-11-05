from templates_app.models.product import Product
import csv


def log_database_state_to_csv(output_file="database_state.csv"):
    """
    Log the database state to CSV format.
    Pros: Easy to open in Excel/spreadsheets, good for analysis
    Cons: Flattened structure (intakes are comma-separated)
    """
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(
            [
                "Product Label",
                "Servings",
                "Duration Value",
                "Duration Unit",
                "Intakes (quantity:frequency)",
            ]
        )

        # Write data rows
        for product in Product.objects.all().order_by("id"):
            first_scheme = product.posology_schemes.all().order_by("order").first()

            label = str(product.label) if product.label else ""
            servings = product.servings

            if first_scheme:
                duration_value = first_scheme.duration_value or ""
                duration_unit = first_scheme.duration_unit or ""

                # Format intakes as "qty:freq, qty:freq, ..."
                intakes = first_scheme.intakes.all().order_by("order")
                intakes_str = ", ".join(
                    [
                        f"{float(intake.quantity)}:{intake.frequency}"
                        for intake in intakes
                    ]
                )
            else:
                duration_value = ""
                duration_unit = ""
                intakes_str = ""

            writer.writerow(
                [
                    label,
                    servings,
                    duration_value,
                    duration_unit,
                    intakes_str,
                ]
            )

    print(f"Database state logged to {output_file}")

