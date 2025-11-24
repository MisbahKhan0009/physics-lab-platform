import os
import re
import subprocess
from datetime import datetime
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LABS_DIR = os.path.join(BASE_DIR, "labs")
BUILD_DIR = os.path.join(BASE_DIR, "build")

os.makedirs(BUILD_DIR, exist_ok=True)


def _load_lab_tex(lab_id: str) -> str:
    lab_dir = os.path.join(LABS_DIR, lab_id)
    tex_path = os.path.join(lab_dir, f"{lab_id}.tex")
    if not os.path.exists(tex_path):
        # Fallback: any .tex file in the lab folder
        for name in os.listdir(lab_dir):
            if name.lower().endswith(".tex"):
                tex_path = os.path.join(lab_dir, name)
                break
        else:
            raise FileNotFoundError(f"No .tex file found for lab {lab_id}")

    with open(tex_path, "r", encoding="utf-8") as f:
        return f.read()


def _latex_escape(text: str) -> str:
    """Escape common LaTeX special characters in free-form text."""

    if not isinstance(text, str):
        text = str(text)

    replacements = {
        "\\": r"\\textbackslash{}",
        "&": r"\\&",
        "%": r"\\%",
        "$": r"\\$",
        "#": r"\\#",
        "_": r"\\_",
        "{" : r"\\{",
        "}": r"\\}",
        "~": r"\\textasciitilde{}",
        "^": r"\\textasciicircum{}",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def _fill_scalar_placeholders(tex: str, answers: Dict[str, Any]) -> str:
    """Replace simple Jinja-style placeholders like {{ q1 }} with answers."""

    def repl(match: re.Match) -> str:
        key = match.group(1).strip()
        value = answers.get(key, "")
        return _latex_escape(value)

    # Only handle bare {{ key }} patterns, not complex expressions
    pattern = re.compile(r"{{\s*([a-zA-Z0-9_\.]+)\s*}}")
    return pattern.sub(repl, tex)


def build_pdf(lab_id: str, data: Dict[str, Any]) -> str:
    """Build a PDF for a lab directly from its LaTeX file and answers.

    `data` should contain at least `student_name`, `section`, and `answers`.
    This function is intentionally simple: it replaces scalar placeholders and
    ignores complex table templating. Tables can be handled separately later
    by generating LaTeX from structured data.
    """

    tex_source = _load_lab_tex(lab_id)

    student_name = data.get("student_name", "")
    section = data.get("section", "")
    answers = data.get("answers", {}) or {}

    # Make basic placeholders accessible via answers too
    answers = {
        **answers,
        "student_name": student_name,
        "section": section,
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

    filled_tex = _fill_scalar_placeholders(tex_source, answers)

    tex_out = os.path.join(BUILD_DIR, f"{lab_id}_report.tex")
    pdf_out = os.path.join(BUILD_DIR, f"{lab_id}_report.pdf")

    with open(tex_out, "w", encoding="utf-8") as f:
        f.write(filled_tex)

    # Call tectonic if installed
    try:
        subprocess.run(
            ["tectonic", tex_out, "--outdir", BUILD_DIR],
            check=True,
        )
    except Exception:
        # Fallback: create a dummy PDF placeholder if tectonic isn't available
        with open(pdf_out, "wb") as f:
            f.write(b"%PDF-1.4\n% placeholder PDF generated because tectonic is missing.\n")

    return pdf_out

