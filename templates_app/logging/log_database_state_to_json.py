from templates_app.models.product import Product
import json


def log_database_state_to_json(output_file="database_state.json"):
    """
    Log the database state after being populated with:
    - Product: label, servings
    - First posology scheme: duration
    - Intakes: quantity and frequency
    """
    products_data = []

    for product in Product.objects.all().order_by("id"):
        # Get the first posology scheme (ordered by order field)
        first_scheme = product.posology_schemes.all().order_by("order").first()

        product_data = {
            "label": str(product.label) if product.label else None,
            "servings": product.servings,
        }

        if first_scheme:
            product_data["first_posology_scheme"] = {
                "duration_value": first_scheme.duration_value,
                "duration_unit": first_scheme.duration_unit,
            }

            # Get all intakes for this scheme
            intakes = first_scheme.intakes.all().order_by("order")
            product_data["intakes"] = [
                {
                    "quantity": float(intake.quantity),
                    "frequency": intake.frequency,
                }
                for intake in intakes
            ]
        else:
            product_data["first_posology_scheme"] = None
            product_data["intakes"] = []

        products_data.append(product_data)

    # Write to JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(products_data, f, indent=2, ensure_ascii=False)

    print(f"Database state logged to {output_file}")
    return products_data

