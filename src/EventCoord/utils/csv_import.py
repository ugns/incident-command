import csv
import io
from typing import Any, Dict, Iterable, List, Optional, Tuple


def parse_csv_rows(csv_text: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    reader = csv.DictReader(io.StringIO(csv_text))
    for row in reader:
        cleaned: Dict[str, Any] = {}
        for key, value in row.items():
            if key is None:
                continue
            normalized_key = key.strip()
            if not normalized_key:
                continue
            if isinstance(value, str):
                cleaned[normalized_key] = value.strip()
            else:
                cleaned[normalized_key] = value
        if any(value not in ("", None) for value in cleaned.values()):
            rows.append(cleaned)
    return rows


def build_natural_key(row: Dict[str, Any], fields: Iterable[str]) -> Optional[Tuple[str, ...]]:
    parts: List[str] = []
    for field in fields:
        value = row.get(field)
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
            parts.append(value.lower())
        else:
            parts.append(str(value))
    return tuple(parts)


def prune_empty_fields(row: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in row.items() if value not in ("", None)}
