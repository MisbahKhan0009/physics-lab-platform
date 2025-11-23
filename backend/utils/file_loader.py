import os
from .latex_to_html import latex_to_html

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LABS_DIR = os.path.join(BASE_DIR, "labs")

PREFERRED_FILENAMES = (
    "instructions.tex",
    "lab.tex",
    "content.tex",
)


def _resolve_lab_tex_path(lab_id: str) -> str:
    lab_dir = os.path.join(LABS_DIR, lab_id)
    if not os.path.isdir(lab_dir):
        raise FileNotFoundError(f"Lab directory not found: {lab_id}")

    # Try preferred filenames first (order matters)
    for name in PREFERRED_FILENAMES:
        candidate = os.path.join(lab_dir, name)
        if os.path.exists(candidate):
            return candidate

    # Fallback: pick the first .tex file in the folder (sorted for determinism)
    tex_files = sorted(
        f for f in os.listdir(lab_dir)
        if f.lower().endswith(".tex") and not f.startswith(".")
    )
    if tex_files:
        return os.path.join(lab_dir, tex_files[0])

    raise FileNotFoundError(
        f"No .tex file found for lab '{lab_id}'. Add instructions.tex or lab.tex."
    )

def load_lab_tex(lab_id: str) -> str:
    path = _resolve_lab_tex_path(lab_id)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_lab_html(lab_id: str) -> str:
    tex = load_lab_tex(lab_id)
    return latex_to_html(tex)
