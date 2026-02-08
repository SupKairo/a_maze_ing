from typing import Any, Dict, List


def read_config(filename: str) -> Dict[str, Any]:
    config: Dict[str, Any] = {}

    try:
        with open(filename, "r") as config_file:
            for line in config_file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    raise ValueError(f"Invalid line (missing '='): {line}")

                key, raw_value = line.split("=", 1)
                value: Any = raw_value

                if key == "WIDTH" or key == "HEIGHT":
                    value = int(raw_value)

                elif key == "ENTRY" or key == "EXIT":
                    parts = raw_value.split(",")
                    if len(parts) != 2:
                        raise ValueError(f"{key} must be in format x,y")
                    value = tuple(int(p) for p in parts)

                elif key == "PERFECT":
                    raw = raw_value.strip().lower()
                    if raw == "true":
                        value = True
                    elif raw == "false":
                        value = False
                    else:
                        raise ValueError("PERFECT must be True or False")

                config[key] = value

    except FileNotFoundError:
        raise FileNotFoundError(f"{filename} File Not Found...")

    return config


def validation(config: Dict[str, Any]) -> None:
    required_keys: List[str] = [
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
        ]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

    for key in config:
        if key not in required_keys:
            raise ValueError(f"Unknown config key: {key}")

    width = config["WIDTH"]
    height = config["HEIGHT"]
    entry = config["ENTRY"]
    exit_ = config["EXIT"]

    if width <= 0 or height <= 0:
        raise ValueError("WIDTH and HEIGHT must be greater than 0")

    if not isinstance(entry, tuple) or not isinstance(exit_, tuple):
        raise ValueError("ENTRY and EXIT must be tuples")

    if len(entry) != 2 or len(exit_) != 2:
        raise ValueError("ENTRY and EXIT must contain exactly 2 values")

    x1, y1 = entry
    x2, y2 = exit_

    if not (0 <= x1 < width and 0 <= y1 < height):
        raise ValueError("ENTRY is outside maze bounds")

    if not (0 <= x2 < width and 0 <= y2 < height):
        raise ValueError("EXIT is outside maze bounds")

    if entry == exit_:
        raise ValueError("ENTRY and EXIT cannot be the same")
