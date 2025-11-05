from datetime import datetime

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def log_randomized_sample_to_yaml(sample, output_file="randomized_sample.yaml"):
    """
    Log the randomized products sample to a separate YAML file.

    Args:
        sample: The actual sample data to log (list of product dicts)
        labels: List of all available product labels
        output_file: Output file path
    """
    if not YAML_AVAILABLE:
        raise ImportError(
            "PyYAML is required for YAML export. Install it with: pip install pyyaml"
        )

    yaml_data = {
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "total_products_in_sample": len(sample),
        },
        "sample": sample,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(
            yaml_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )

    print(f"Randomized sample logged to {output_file}")
    return sample
