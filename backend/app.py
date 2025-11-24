from flask import Flask, jsonify, request, send_file
from utils.pdf_builder import build_pdf
from utils.file_loader import load_lab_html
from utils.lab_parser import get_lab_structure
import os
import json

app = Flask(__name__)

LABS_DIR = os.path.join(os.path.dirname(__file__), "labs")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

@app.get("/labs")
def list_labs():
    labs = [
        name for name in os.listdir(LABS_DIR)
        if os.path.isdir(os.path.join(LABS_DIR, name))
    ]
    return jsonify(labs)

@app.get("/lab/<lab_id>/html")
def get_lab_html(lab_id):
    html = load_lab_html(lab_id)
    return {"html": html}


@app.get("/lab/<lab_id>/structure")
def get_lab_structure_endpoint(lab_id):
    """Return rendered HTML plus field metadata for a lab.

    This is used by the frontend to build dynamic input fields, tables, etc.
    """
    data = get_lab_structure(lab_id)
    return jsonify(data)

@app.post("/lab/<lab_id>/pdf")
def generate_pdf(lab_id):
    data = request.json or {}
    pdf_path = build_pdf(lab_id, data)

    # Build filename: Lab<nr>-First_Last.pdf
    student_name = data.get("student_name", "Student").strip() or "Student"
    lab_number = "".join(ch for ch in lab_id if ch.isdigit()) or lab_id

    def sanitize_name(name: str) -> str:
        return "_".join(part for part in name.split() if part)

    safe_name = sanitize_name(student_name)
    filename = f"Lab{lab_number}-{safe_name}.pdf"

    return send_file(pdf_path, as_attachment=True, download_name=filename)


@app.post("/lab/<lab_id>/save")
def save_answers(lab_id):
    payload = request.json or {}
    student_name = (payload.get("student_name") or "").strip()
    section = (payload.get("section") or "").strip()
    answers = payload.get("answers") or {}

    if not student_name or not section:
        return jsonify({"error": "student_name and section are required for saving"}), 400

    lab_dir = os.path.join(DATA_DIR, lab_id)
    os.makedirs(lab_dir, exist_ok=True)

    key = f"{student_name}__{section}".replace(os.sep, "_")
    path = os.path.join(lab_dir, f"{key}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump({"student_name": student_name, "section": section, "answers": answers}, f)

    return jsonify({"status": "saved"})


@app.post("/lab/<lab_id>/load")
def load_answers(lab_id):
    payload = request.json or {}
    student_name = (payload.get("student_name") or "").strip()
    section = (payload.get("section") or "").strip()

    if not student_name or not section:
        return jsonify({"answers": {}})

    lab_dir = os.path.join(DATA_DIR, lab_id)
    key = f"{student_name}__{section}".replace(os.sep, "_")
    path = os.path.join(lab_dir, f"{key}.json")

    if not os.path.exists(path):
        return jsonify({"answers": {}})

    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)

    return jsonify({"answers": obj.get("answers", {})})

if __name__ == "__main__":
    app.run(port=5001, debug=True)
