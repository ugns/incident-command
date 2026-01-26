import csv
import io
import json
from typing import Any, Iterable, Mapping, Sequence


def _normalize_csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, separators=(",", ":"), ensure_ascii=True)
    return str(value)


def items_to_csv(
    items: Sequence[Mapping[str, Any]],
    exclude_fields: Iterable[str],
) -> str:
    exclude = set(exclude_fields)
    if not items:
        return ""
    fieldnames = sorted(
        {key for item in items for key in item.keys() if key not in exclude}
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(fieldnames)
    for item in items:
        row = [_normalize_csv_value(item.get(name)) for name in fieldnames]
        writer.writerow(row)
    return output.getvalue()
