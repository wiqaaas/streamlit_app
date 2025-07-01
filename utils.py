import json

def chunk_json(json_str: str, max_chars: int = 50_000) -> list:
    """
    Split a big JSON string into chunks each ≤ max_chars.
    """
    return [json_str[i : i + max_chars] for i in range(0, len(json_str), max_chars)]
