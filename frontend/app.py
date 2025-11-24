import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

BACKEND = "http://localhost:5001"

st.title("Physics Lab Platform")

MATHJAX_SNIPPET = """
<script>
window.MathJax = {
  tex: { inlineMath: [['$', '$'], ['\\\\(', '\\\\)']] },
  svg: { fontCache: 'global' }
};
</script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
"""

# Inject MathJax into the page once
# st.markdown(MATHJAX_SNIPPET, unsafe_allow_html=True)

# Load labs
try:
    labs = requests.get(f"{BACKEND}/labs", timeout=5).json()
except Exception as e:
    st.error(f"Could not connect to backend at {BACKEND}: {e}")
    st.stop()

lab = st.selectbox("Choose a lab", labs)

# Auto-refresh to enable background autosave without user clicks
st_autorefresh = st.experimental_rerun if False else None  # placeholder to avoid linter warnings

# Load structured lab definition (HTML + fields)
resp = requests.get(f"{BACKEND}/lab/{lab}/structure")
data = resp.json()
html = data.get("html", "")
field_defs = data.get("fields", [])

components.html(html, height=800, scrolling=True)

st.subheader("Student Info")

if "answers" not in st.session_state:
    st.session_state["answers"] = {}
if "last_autosave" not in st.session_state:
    st.session_state["last_autosave"] = 0.0

answers = st.session_state["answers"]


def get_answer(field_id, default=""):
    return answers.get(field_id, default)


student_name = st.text_input("Student name", value=get_answer("student_name"))
answers["student_name"] = student_name

section = st.text_input("Section", value=get_answer("section"))
answers["section"] = section

# Attempt to load any existing answers once we know identity
if student_name and section and not answers.get("_loaded_once"):
    try:
        r = requests.post(
            f"{BACKEND}/lab/{lab}/load",
            json={"student_name": student_name, "section": section},
            timeout=3,
        )
        if r.status_code == 200:
            loaded = r.json().get("answers", {})
            # Merge, but don't overwrite anything the student already typed this session
            for k, v in loaded.items():
                answers.setdefault(k, v)
        answers["_loaded_once"] = True
    except Exception:
        pass

st.subheader("Lab Fields")

tables: dict[str, pd.DataFrame] = {}

for f in field_defs:
    fid = f.get("id")
    ftype = f.get("type")
    label = f.get("label", fid)

    # Skip name/section here; we already rendered them
    if fid in {"student_name", "section"}:
        continue

    if ftype == "text":
        val = st.text_input(label, value=get_answer(fid, ""), key=fid)
        answers[fid] = val
    elif ftype == "textarea":
        val = st.text_area(label, value=get_answer(fid, ""), key=fid)
        answers[fid] = val
    elif ftype == "table":
        cols = f.get("columns", [])
        existing = answers.get(fid)
        if isinstance(existing, dict) and "data" in existing and "columns" in existing:
            df_init = pd.DataFrame(existing["data"], columns=existing["columns"])
        else:
            df_init = pd.DataFrame({c: [] for c in cols})

        df = st.data_editor(df_init, num_rows="dynamic", key=fid)
        tables[fid] = df
        answers[fid] = {"columns": list(df.columns), "data": df.to_dict(orient="records")}

        if not df.empty:
            # Simple default: plot first two numeric columns if available
            numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            if len(numeric_cols) >= 2:
                x_col, y_col = numeric_cols[0], numeric_cols[1]
                st.caption(f"Auto-plot: {x_col} vs {y_col}")
                fig, ax = plt.subplots()
                ax.scatter(df[x_col], df[y_col])
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                st.pyplot(fig)


# Autosave every ~10 seconds in the background (best-effort)
now = time.time()
if student_name and section and (now - st.session_state["last_autosave"] > 10):
    try:
        payload = {
            "student_name": student_name,
            "section": section,
            "answers": answers,
        }
        requests.post(f"{BACKEND}/lab/{lab}/save", json=payload, timeout=3)
        st.session_state["last_autosave"] = now
    except Exception:
        # Silent failure; we don't want to interrupt the student
        pass


st.subheader("Generate PDF")

if st.button("Generate PDF report"):
    payload = {
        "student_name": student_name,
        "section": section,
        "answers": answers,
    }

    with st.spinner("Requesting PDF from backend..."):
        r = requests.post(f"{BACKEND}/lab/{lab}/pdf", json=payload)
    if r.status_code == 200:
        st.success("PDF generated!")
        # Filename will be set by backend; use its headers if available
        default_name = r.headers.get("Content-Disposition", "lab_report.pdf")
        st.download_button(
            "Download PDF",
            data=r.content,
            file_name="lab_report.pdf",
            mime="application/pdf",
        )
    else:
        st.error(f"Backend error: {r.status_code} - {r.text}")
