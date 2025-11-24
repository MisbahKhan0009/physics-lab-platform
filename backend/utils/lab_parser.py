import os
import re
from typing import Dict, Any, List, Tuple

from .latex_to_html import latex_to_html


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LABS_DIR = os.path.join(BASE_DIR, "labs")


FIELD_PATTERN = re.compile(r"FIELD:([a-zA-Z0-9_]+):([a-zA-Z0-9_]+)")
TABLE_PATTERN = re.compile(r"TABLE:([a-zA-Z0-9_]+):columns=([a-zA-Z0-9_,]+)")


def load_lab_source(lab_id: str) -> str:
    lab_dir = os.path.join(LABS_DIR, lab_id)
    tex_path = os.path.join(lab_dir, f"{lab_id}.tex")
    if not os.path.exists(tex_path):
        # Fallback to any .tex inside the folder (e.g., lab3_report.tex)
        for name in os.listdir(lab_dir):
            if name.lower().endswith(".tex"):
                tex_path = os.path.join(lab_dir, name)
                break
        else:
            raise FileNotFoundError(f"No .tex file found for lab {lab_id}")

    with open(tex_path, "r", encoding="utf-8") as f:
        return f.read()


def parse_fields(tex_source: str) -> List[Dict[str, Any]]:
    """Extract FIELD and TABLE markers from a LaTeX source.

    Returns a list of dictionaries with keys: id, type, label, and optional columns.
    """

    fields: Dict[str, Dict[str, Any]] = {}

    lines = tex_source.splitlines()
    for line in lines:
        # FIELD markers can appear after LaTeX content, so just search the whole line
        for match in FIELD_PATTERN.finditer(line):
            field_id, field_type = match.group(1), match.group(2)
            if field_id not in fields:
                # Use field_id as label by default; UI can prettify
                fields[field_id] = {
                    "id": field_id,
                    "type": "textarea" if field_type.lower() == "textarea" else "text",
                    "label": field_id,
                }

        for match in TABLE_PATTERN.finditer(line):
            table_id, cols = match.group(1), match.group(2)
            columns = [c.strip() for c in cols.split(",") if c.strip()]
            if table_id not in fields:
                fields[table_id] = {
                    "id": table_id,
                    "type": "table",
                    "label": table_id,
                    "columns": columns,
                }

    return list(fields.values())


def get_lab_structure(lab_id: str) -> Dict[str, Any]:
    """Return HTML plus structured field metadata for a lab."""

    tex_source = load_lab_source(lab_id)
    html = latex_to_html(tex_source)
    fields = parse_fields(tex_source)

    return {
        "html": html,
        "fields": fields,
    }
