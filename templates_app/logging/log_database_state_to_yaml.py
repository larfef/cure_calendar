from templates_app.models.product import Product
from datetime import datetime

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def log_database_state_to_yaml(output_file="database_state.yaml"):
    """
    Log the database state to YAML format.
    Pros: Human-readable, supports comments, better for config files
    Cons: Requires PyYAML package (pip install pyyaml)
    """
    if not YAML_AVAILABLE:
        raise ImportError(
            "PyYAML is required for YAML export. Install it with: pip install pyyaml"
        )

    products_data = []

    for product in Product.objects.all().order_by("id"):
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

    # Add metadata comment
    yaml_data = {
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "total_products": len(products_data),
        },
        "products": products_data,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(
            yaml_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )

    print(f"Database state logged to {output_file}")
    return products_data
