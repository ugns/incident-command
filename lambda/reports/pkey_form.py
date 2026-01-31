#!/usr/bin/env python3
from __future__ import annotations

import datetime as _dt
import io
import os
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth

MEDIA_TYPE = "application/pdf"
TITLE = "Prize Key Form"


# ----------------------------
# Row normalization
# ----------------------------

def _norm_header(s: object) -> str:
    if s is None:
        return ""
    return " ".join(str(s).strip().split()).lower()


def pick_value(row: Dict[str, object], *candidates: str) -> Optional[object]:
    for key in candidates:
        k = _norm_header(key)
        if k and k in row:
            v = row.get(k)
            if v not in (None, ""):
                return v
    return None


# ----------------------------
# Drawing formatting
# ----------------------------

def format_day_abbr(day_val: object) -> str:
    if day_val in (None, ""):
        return ""
    return str(day_val).strip()[:3].title()


def format_time_24h_hhmm(time_val: object) -> str:
    if time_val in (None, ""):
        return ""

    if isinstance(time_val, _dt.datetime):
        return time_val.strftime("%H:%M")
    if isinstance(time_val, _dt.time):
        return time_val.strftime("%H:%M")

    if isinstance(time_val, (int, float)):
        tv = float(time_val)
        if 0 <= tv < 1:
            total_minutes = int(round(tv * 24 * 60))
            hh = (total_minutes // 60) % 24
            mm = total_minutes % 60
            return f"{hh:02d}:{mm:02d}"

    s = str(time_val).strip()
    if "T" in s:
        try:
            dt = _dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
            return dt.strftime("%H:%M")
        except Exception:
            pass
    for fmt in ("%H:%M", "%H:%M:%S", "%H%M", "%H%M%S", "%I:%M %p", "%I:%M:%S %p"):
        try:
            t = _dt.datetime.strptime(s, fmt).time()
            return t.strftime("%H:%M")
        except ValueError:
            pass

    if ":" in s:
        parts = s.split(":")
        try:
            hh = int(parts[0])
            mm = int(parts[1])
            return f"{hh:02d}:{mm:02d}"
        except Exception:
            return s

    return s


# ----------------------------
# Batching + field map
# ----------------------------

def chunked(seq: Sequence[Dict[str, object]], n: int) -> Iterable[List[Dict[str, object]]]:
    for i in range(0, len(seq), n):
        yield list(seq[i:i + n])


def build_batch_field_map(batch_rows: List[Dict[str, object]], *, slots: int = 10) -> Dict[str, str]:
    fields: Dict[str, str] = {}

    for i in range(slots):
        fields[f"PKEY_{i}"] = ""
        fields[f"Prize_{i}"] = ""
        fields[f"Drawing_{i}"] = ""
        fields[f"Donated_{i}"] = ""
        fields[f"Comments_{i}"] = ""

    for i, row in enumerate(batch_rows[:slots]):
        pkey = pick_value(row, "pkey")
        prize = pick_value(row, "prize")
        day = pick_value(row, "day")
        time = pick_value(row, "time")
        donated = pick_value(row, "donated by", "donated_by", "donor", "donated", "donatedby")
        comments = pick_value(row, "comments", "winner", "note", "notes")

        drawing = pick_value(row, "drawing", "draw", "draw time", "draw_time")
        if drawing in (None, ""):
            drawing = f"{format_day_abbr(day)} {format_time_24h_hhmm(time)}".strip()
        else:
            drawing = str(drawing).strip()

        fields[f"PKEY_{i}"] = "" if pkey in (None, "") else str(pkey).strip()

        if prize in (None, ""):
            fields[f"Prize_{i}"] = ""
        else:
            prize_str = str(prize).strip()
            fields[f"Prize_{i}"] = prize_str[:64]  # truncate to 64 chars

        fields[f"Drawing_{i}"] = drawing
        fields[f"Donated_{i}"] = "" if donated in (None, "") else str(donated).strip()
        fields[f"Comments_{i}"] = "" if comments in (None, "") else str(comments).strip()

    return fields


# ----------------------------
# Overlay "flattening" with robust field inheritance + normalized names
# ----------------------------

MULTILINE_FLAG_BIT = 1 << 12  # PDF spec: multiline is bit 13 (0-based 12)

DA_FONT_MAP = {
    "/Helv": "Helvetica",
    "/Helvetica": "Helvetica",
    "/Times-Roman": "Times-Roman",
    "/Courier": "Courier",
}


def _clean_pdf_field_name(name: object) -> str:
    """
    Normalize PDF field names to avoid hidden-character mismatches.
    Fixes common issues: trailing spaces, NBSP, NULs.
    """
    if name is None:
        return ""
    s = str(name)
    s = s.replace("\x00", "")          # NUL
    s = s.replace("\u00A0", " ")       # NBSP -> space
    s = s.strip()
    return s


def _inherit_get(obj, key: NameObject):
    cur = obj
    while cur is not None:
        if key in cur:
            return cur.get(key)
        parent = cur.get(NameObject("/Parent"))
        if parent is None:
            break
        cur = parent.get_object()
    return None


def _resolve_field_name(widget_annot) -> str:
    t = _inherit_get(widget_annot, NameObject("/T"))
    return _clean_pdf_field_name(t)


def _effective_flags(widget_annot) -> int:
    ff = _inherit_get(widget_annot, NameObject("/Ff"))
    try:
        return int(ff)
    except Exception:
        return 0


def _effective_alignment(widget_annot) -> int:
    q = _inherit_get(widget_annot, NameObject("/Q"))
    try:
        return int(q)
    except Exception:
        return 0  # left


def _parse_DA_font_and_size(da_val) -> Tuple[str, float]:
    if not da_val:
        return ("Helvetica", 9.0)

    da = str(da_val)
    parts = da.replace("\n", " ").split()

    for i in range(len(parts) - 2):
        if parts[i].startswith("/") and parts[i + 2] == "Tf":
            font_token = parts[i]
            try:
                size = float(parts[i + 1])
            except Exception:
                size = 9.0

            font_name = DA_FONT_MAP.get(font_token, font_token.lstrip("/"))
            return (font_name, size)

    return ("Helvetica", 9.0)


def _rect_to_box(rect) -> Tuple[float, float, float, float]:
    llx, lly, urx, ury = [float(x) for x in rect]
    x = min(llx, urx)
    y = min(lly, ury)
    w = abs(urx - llx)
    h = abs(ury - lly)
    return x, y, w, h


def _wrap_preserving_newlines(text: str, font_name: str, font_size: float, max_width: float) -> List[str]:
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = text.split("\n")

    lines: List[str] = []
    for para in paragraphs:
        words = para.split()
        if not words:
            lines.append("")
            continue

        cur = words[0]
        for w in words[1:]:
            trial = f"{cur} {w}"
            if stringWidth(trial, font_name, font_size) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)

    return lines


def overlay_fill_and_flatten(template_pdf: str, field_values: Dict[str, str], *, debug: bool = False) -> PdfWriter:
    """
    Print-ready flattening:
      - draws values into widget rects using inherited /Q, /Ff, /DA
      - removes widget annotations and AcroForm
      - uses normalized field-name matching to avoid hidden-char bugs (e.g., PKEY_1)
    """
    # Normalize keys once (this is the important fix for "PKEY_1 missing")
    values_norm: Dict[str, str] = {_clean_pdf_field_name(k): ("" if v is None else str(v)) for k, v in field_values.items()}

    reader = PdfReader(template_pdf)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    padding = 1.5
    leading_mult = 1.15

    seen_names: set[str] = set()

    for page in writer.pages:
        annots = page.get(NameObject("/Annots"))
        if not annots:
            continue

        packet = io.BytesIO()
        page_w = float(page.mediabox.width)
        page_h = float(page.mediabox.height)
        c = canvas.Canvas(packet, pagesize=(page_w, page_h))

        for annot_ref in list(annots):
            annot = annot_ref.get_object()
            if annot.get(NameObject("/Subtype")) != NameObject("/Widget"):
                continue

            field_name = _resolve_field_name(annot)
            if not field_name:
                continue

            seen_names.add(field_name)

            if field_name not in values_norm:
                continue

            rect = annot.get(NameObject("/Rect"))
            if not rect:
                continue

            ff = _effective_flags(annot)
            is_multiline = bool(ff & MULTILINE_FLAG_BIT)
            align = _effective_alignment(annot)

            da = _inherit_get(annot, NameObject("/DA"))
            font_name, font_size = _parse_DA_font_and_size(da)

            try:
                pdfmetrics.getFont(font_name)
            except Exception:
                font_name = "Helvetica"

            x, y, w, h = _rect_to_box(rect)
            max_text_width = max(1.0, w - 2 * padding)

            value = values_norm.get(field_name, "")
            value = "" if value is None else str(value)

            if is_multiline:
                lines = _wrap_preserving_newlines(value, font_name, font_size, max_text_width)
            else:
                lines = [value.replace("\n", " ").replace("\r", " ")]

            c.setFont(font_name, font_size)

            line_h = font_size * leading_mult
            start_y = y + h - padding - font_size

            for li, line in enumerate(lines):
                draw_y = start_y - li * line_h
                if draw_y < y + padding:
                    break

                if align == 1:
                    c.drawCentredString(x + w / 2.0, draw_y, line)
                elif align == 2:
                    c.drawRightString(x + w - padding, draw_y, line)
                else:
                    c.drawString(x + padding, draw_y, line)

        c.showPage()
        c.save()
        packet.seek(0)

        overlay_pdf = PdfReader(packet)
        page.merge_page(overlay_pdf.pages[0], over=True)

        # Remove widget annotations
        new_annots = []
        for annot_ref in list(annots):
            a = annot_ref.get_object()
            if a.get(NameObject("/Subtype")) != NameObject("/Widget"):
                new_annots.append(annot_ref)

        if new_annots:
            page[NameObject("/Annots")] = new_annots
        else:
            page.pop(NameObject("/Annots"), None)

    if debug:
        # Helps confirm whether PDF field name has hidden chars:
        # If you see "PKEY_1 " or similar in this list, that's the root cause.
        missing = [k for k in values_norm.keys() if k not in seen_names]
        if missing:
            print("DEBUG: keys in field_values not seen in PDF widgets:", missing)
        # Also print the exact PKEY_1 seen in the PDF, if any
        for s in sorted(seen_names):
            if "PKEY_1" in s:
                print(f"DEBUG: PDF widget field name contains: {repr(s)}")

    # Remove AcroForm (not fillable)
    try:
        writer._root_object.pop(NameObject("/AcroForm"), None)
    except Exception:
        pass

    return writer


def write_combined_pdf_printready(
    template_pdf: str,
    batches: List[List[Dict[str, object]]],
    out_pdf: str,
    batch_size: int,
    *,
    debug: bool = False,
) -> None:
    master = PdfWriter()
    for batch in batches:
        field_map = build_batch_field_map(batch, slots=batch_size)
        filled_flat = overlay_fill_and_flatten(template_pdf, field_map, debug=debug)
        for p in filled_flat.pages:
            master.add_page(p)

    os.makedirs(os.path.dirname(out_pdf) or ".", exist_ok=True)
    with open(out_pdf, "wb") as f:
        master.write(f)


def _normalize_row(row: Dict[str, object]) -> Dict[str, object]:
    normalized: Dict[str, object] = {}
    for key, value in row.items():
        nk = _norm_header(key)
        if not nk:
            continue
        normalized[nk] = value
    return normalized


def _extract_rows(data: Any) -> List[Dict[str, object]]:
    if isinstance(data, list):
        return [_normalize_row(row) for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        for key in ("rows", "entries", "prizes", "items", "data"):
            value = data.get(key)
            if isinstance(value, list):
                return [_normalize_row(row) for row in value if isinstance(row, dict)]
    return []


def generate_report(data: Any) -> bytes:
    template_pdf = os.environ.get("PKEY_TEMPLATE_PDF")
    if not template_pdf:
        template_pdf = os.path.join(os.path.dirname(__file__), "HamcationPrizeInfo.pdf")

    rows = _extract_rows(data)
    if not rows:
        raise ValueError("No rows provided for prize key report.")

    batch_size = 10
    if isinstance(data, dict):
        try:
            batch_size = int(data.get("batchSize", batch_size))
        except Exception:
            batch_size = 10
    if batch_size <= 0:
        batch_size = 10

    batches = list(chunked(rows, batch_size))
    master = PdfWriter()
    for batch in batches:
        field_map = build_batch_field_map(batch, slots=batch_size)
        filled_flat = overlay_fill_and_flatten(template_pdf, field_map, debug=False)
        for p in filled_flat.pages:
            master.add_page(p)

    buffer = io.BytesIO()
    master.write(buffer)
    buffer.seek(0)
    return buffer.read()
