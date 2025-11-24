from flask import Flask, jsonify, request, send_file
from utils.pdf_builder import build_pdf
from utils.file_loader import load_lab_html
from utils.lab_parser import get_lab_structure
import os

app = Flask(__name__)

LABS_DIR = os.path.join(os.path.dirname(__file__), "labs")

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
    return send_file(pdf_path, as_attachment=True, download_name="lab_report.pdf")

if __name__ == "__main__":
    app.run(port=5001, debug=True)
