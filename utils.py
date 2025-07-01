import json

def chunk_json(js: str, max_chars: int = 50_000) -> list[str]:
    """
    Split a big JSON string into chunks each ≤ max_chars long.
    """
    return [js[i : i + max_chars] for i in range(0, len(js), max_chars)]
