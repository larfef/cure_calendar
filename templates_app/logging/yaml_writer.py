from pathlib import Path
import yaml


def write_products_to_yaml(data, output_path="products_output.yaml"):
    """Write calculator products to YAML file."""

    output_file = Path(output_path)
    with output_file.open("w", encoding="utf-8") as f:
        yaml.dump(
            data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )

    return str(output_file.absolute())
