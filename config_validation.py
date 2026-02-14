from typing import Any, Dict, List


def read_config(filename: str) -> Dict[str, Any]:
    """Read and parse maze configuration file into a dictionary."""
    config: Dict[str, Any] = {}

    try:
        with open(filename, "r") as config_file:
            for line in config_file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    raise ValueError(f"Invalid format (missing '='): {line}")

                key, raw_value = line.split("=", 1)
                key = key.strip().upper()
                raw_value = raw_value.strip()

                if not raw_value:
                    raise ValueError(f"{key} cannot be empty")

                value: Any = raw_value

                if key in ("WIDTH", "HEIGHT"):
                    try:
                        value = int(raw_value)
                    except ValueError:
                        raise ValueError(f"{key} must be an integer")

                elif key in ("ENTRY", "EXIT"):
                    parts = raw_value.split(",")
                    if len(parts) != 2:
                        raise ValueError(f"{key} must be in format x,y")
                    try:
                        value = tuple(int(p.strip()) for p in parts)
                    except ValueError:
                        raise ValueError(f"{key} coordinates must be integers")

                elif key == "PERFECT":
                    raw = raw_value.strip().lower()
                    if raw == "true":
                        value = True
                    elif raw == "false":
                        value = False
                    else:
                        raise ValueError("PERFECT must be True or False")

                elif key == "SEED":
                    try:
                        value = int(raw_value)
                    except ValueError:
                        raise ValueError("SEED must be an integer")

                elif key == "OUTPUT_FILE":
                    value = raw_value

                config[key] = value

    except FileNotFoundError:
        raise FileNotFoundError(f"{filename} not found")

    return config


def validation(config: Dict[str, Any]) -> None:
    """Validate configuration parameters and check for errors."""
    required_keys: List[str] = [
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
    ]

    optional_keys: List[str] = ["SEED"]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

    for key in config:
        if key not in required_keys and key not in optional_keys:
            raise ValueError(f"Unknown config key: {key}")

    width = config["WIDTH"]
    height = config["HEIGHT"]
    entry = config["ENTRY"]
    exit_ = config["EXIT"]
    output_file = config["OUTPUT_FILE"]

    if not isinstance(width, int) or not isinstance(height, int):
        raise ValueError("WIDTH and HEIGHT must be integers")

    if width <= 0 or height <= 0:
        raise ValueError("WIDTH and HEIGHT must be greater than 0")

    if not isinstance(entry, tuple) or not isinstance(exit_, tuple):
        raise ValueError("ENTRY and EXIT must be tuples")

    if len(entry) != 2 or len(exit_) != 2:
        raise ValueError("ENTRY and EXIT must contain exactly 2 values")

    x1, y1 = entry
    x2, y2 = exit_

    if not (0 <= x1 < width and 0 <= y1 < height):
        raise ValueError(f"ENTRY {entry} is outside maze bounds")

    if not (0 <= x2 < width and 0 <= y2 < height):
        raise ValueError(f"EXIT {exit_} is outside maze bounds")

    if entry == exit_:
        raise ValueError("ENTRY and EXIT cannot be the same")

    if not isinstance(output_file, str) or not output_file.strip():
        raise ValueError("OUTPUT_FILE must be a non-empty string")

    if "SEED" in config:
        seed = config["SEED"]
        if not isinstance(seed, int):
            raise ValueError("SEED must be an integer")

    perfect = config["PERFECT"]
    if not isinstance(perfect, bool):
        raise ValueError("PERFECT must be True or False")
