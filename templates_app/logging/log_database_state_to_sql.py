from templates_app.models.product import Product
from datetime import datetime


def log_database_state_to_sql(output_file="database_state.sql"):
    """
    Log the database state as SQL INSERT statements.
    Pros: Can recreate exact database state, version control friendly
    Cons: More verbose, requires SQL knowledge
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("-- Database state export\n")
        f.write(f"-- Exported at: {datetime.now().isoformat()}\n\n")
        f.write("-- Products\n")

        for product in Product.objects.all().order_by("id"):
            label = str(product.label).replace("'", "''") if product.label else "NULL"
            servings = product.servings

            f.write(
                f"INSERT INTO templates_app_product (label, servings) "
                f"VALUES ('{label}', {servings});\n"
            )

        f.write("\n-- Posology Schemes\n")
        for product in Product.objects.all().order_by("id"):
            for scheme in product.posology_schemes.all().order_by("order"):
                duration_value = scheme.duration_value or "NULL"
                duration_unit = (
                    f"'{scheme.duration_unit}'" if scheme.duration_unit else "NULL"
                )

                f.write(
                    f"INSERT INTO templates_app_posologyscheme "
                    f'(product_id, duration_value, duration_unit, "order") '
                    f"VALUES ({product.id}, {duration_value}, {duration_unit}, {scheme.order});\n"
                )

        f.write("\n-- Posology Intakes\n")
        for product in Product.objects.all().order_by("id"):
            for scheme in product.posology_schemes.all().order_by("order"):
                for intake in scheme.intakes.all().order_by("order"):
                    f.write(
                        f"INSERT INTO templates_app_posologyintake "
                        f'(scheme_id, quantity, frequency, "order") '
                        f"VALUES ({scheme.id}, {float(intake.quantity)}, "
                        f"{intake.frequency}, {intake.order});\n"
                    )

    print(f"Database state logged to {output_file}")

