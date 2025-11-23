# Physics Lab Platform

A web-based interactive physics laboratory platform for running, visualizing, and managing physics lab experiments with a Python backend and Streamlit front-end.

## 🚀 Getting Started: Installation & Running the Project

### 1) Clone the Repository

```bash
git clone https://github.com/imusa007/physics-lab-platform.git
cd physics-lab-platform
```

### 2) Option A — Using Conda (recommended)

```bash
conda create -n physics-lab python=3.11 -y
conda activate physics-lab
```

Install project dependencies (both backend & frontend):

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

Install Pandoc (LaTeX → HTML) and optional Tectonic (PDF compiler):

```bash
conda install -c conda-forge pandoc -y
conda install -c conda-forge tectonic -y  # optional but recommended
```

### 2) Option B — Using Python venv (Windows/macOS/Linux)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
pip install -r frontend\requirements.txt
```

Install Pandoc (required) + Tectonic (optional):

- Winget: `winget install JohnMacFarlane.Pandoc` and `winget install Tectonic.Tectonic`
- Chocolatey: `choco install pandoc -y` and `choco install tectonic -y`
- Manual downloads: <https://pandoc.org/installing.html> and <https://tectonic-typesetting.github.io/en-US/>

### 3) Run the Backend (Flask)

```bash
cd backend
python app.py
```

### 4) Run the Frontend (Streamlit)

```bash
cd frontend
streamlit run app.py
```

### 5) Access the Application

- Backend: `http://localhost:5001`
- Frontend: `http://localhost:8501`

If Streamlit shows “Could not connect…”, confirm the backend terminal is running and Pandoc is installed.

### Adding a New Lab (.tex)

1. Create a folder under `backend/labs/` (for example, `backend/labs/lab5`).
2. Add the LaTeX file you want rendered. The backend looks for `instructions.tex`, `lab.tex`, `content.tex`, or the first `.tex` file alphabetically.
3. (Optional) Drop a `template.tex` in the same folder to control PDF output placeholders.
4. Restart the backend (`python backend/app.py`). The new lab will automatically appear in the frontend dropdown and render using the same pipeline as existing labs.

---

# Project Plan


# 📘 **Physics Lab Web App — Project Summary (MVP → Full System Plan)**

_Author: Musa_

---

## 🎯 **Project Goal**

Build a modern, interactive web platform for physics labs that:

- Displays lab instructions (math, images, tables) beautifully online
    
- Lets students input data, plots, and answers
    
- Generates **professional LaTeX-based lab reports**
    
- Allows future upgrades: login system, data storage, class/section management
    
- Works on any device with a browser
    

---

## 🏗️ **High-Level Architecture**

```
                ┌──────────────────┐
                │  LaTeX Lab Files  │
                │(source .tex files)│
                └───────┬──────────┘
                        ▼ convert to HTML (via backend)
                 ┌────────────────────┐
                 │  Backend Server    │
                 │  (FastAPI/Flask)   │
                 │ - Convert LaTeX→HTML
                 │ - Fill LaTeX template
                 │ - Generate PDF w/ Tectonic
                 │ - Student login (future)
                 └───────┬───────────┘
                         ▲ JSON API
                         ▼
                 ┌────────────────────┐
                 │   Streamlit App    │
                 │  (Frontend for students)   
                 │ - Display instructions
                 │ - Render math w/ MathJax
                 │ - Collect data + answers
                 │ - Submit to backend
                 │ - Download PDF
                 └────────────────────┘
```

---

## 📄 **Core Idea**

### **1. You keep authoring labs in LaTeX**

This preserves your workflow and gives:

- equations
    
- diagrams
    
- tables
    
- formatting
    

### **2. The frontend renders those .tex files as HTML**

Via MathJax + HTML conversion so students see:

- Beautiful typeset equations
    
- Graphs
    
- Figures
    
- Clear structure
    

### **3. Students input data + answers**

Tables, numeric inputs, text answers, uploads, plots.

### **4. Backend fills a LaTeX template with student data**

Then compiles to PDF.

### **5. PDF download**

Professional, consistent, printable.

---

## 📂 **Project Components**

### **A. Frontend (Streamlit)**

- Displays HTML-rendered lab instructions
    
- Shows all LaTeX equations using MathJax
    
- Renders tables, images, sections
    
- Provides interactive data table
    
- Auto-generates plots
    
- Sends JSON payload to backend
    
- Downloads PDF returned from backend
    

---

### **B. Backend (FastAPI or Flask)**

**Responsibilities:**

1. Serve the HTML-rendered version of each .tex lab
    
2. Inject student answers into a LaTeX template
    
3. Compile the final PDF using **Tectonic**
    
4. Return PDF to Streamlit
    
5. Future: authentication & storage
    

---

### **C. LaTeX Templates**

Each lab exists as:

```
labs/
  lab1_acceleration.tex
  lab1_template.tex   ← has placeholders
  lab1_assets/
      diagram1.png
      table_example.png
```

**Placeholders**:

```
{{ student_name }}
{{ section }}
{{ data_table }}
{{ analysis }}
{{ conclusion }}
{{ graph_file }}
```

---

## 📦 **Technologies Used**

### **Frontend**

- Streamlit
    
- MathJax (built into Streamlit via HTML)
    
- Pandas / Matplotlib
    
- Axios/Requests for backend communication
    

### **Backend**

- FastAPI (best) or Flask
    
- Jinja2 for LaTeX templating
    
- **Tectonic** for PDF generation
    
- LaTeXML/Pandoc for LaTeX → HTML
    

### **Data Formats**

- Frontend → Backend: JSON
    
- Backend → Frontend: PDF bytes
    

---

## 🧪 **MVP Scope** (You already achieved part)

- Streamlit app
    
- Collect student data
    
- Generate PDF (now: simple FPDF prototype)
    
- Download PDF
    

**Next MVP extension:**

- Replace FPDF with backend LaTeX + Tectonic
    
- Render LaTeX instructions in Streamlit
    
- Add endpoints:
    
    - `/list_labs`
        
    - `/lab/<id>/html`
        
    - `/lab/<id>/render_pdf`
        

---

## 🚀 **Full System (Phase 2)**

### ✔ Student accounts

- JWT login
    
- Google/Microsoft login
    
- Per-class roster
    

### ✔ Instructor dashboard

- See submissions
    
- Grade them (maybe auto-grade some parts)
    
- Export to CSV
    

### ✔ Store submissions

- JSON
    
- Generated PDF
    
- Student metadata
    

### ✔ Versioned labs

- Edit labs in LaTeX
    
- Push to repo
    
- Students always get fresh content
    

---

## 🧭 **Implementation Roadmap**

### **Phase 1 (2–4 weeks)**

- Finalize architecture
    
- Implement backend LaTeX→HTML endpoint
    
- Implement LaTeX PDF generation
    
- Connect Streamlit to backend
    
- Replace FPDF entirely
    
- Render equations in Streamlit
    
- Achieve full PDF lab report generation
    

### **Phase 2 (4–8 weeks)**

- Student login system
    
- Logging & analytics
    
- Save submissions
    
- Instructor backend
    

### **Phase 3**

- Gradebooks
    
- Autorubrics
    
- More advanced plotting capabilities
    
- Multi-tab lab navigation
    
- Mobile-friendly view
    

---

## 🔑 **Key Design Principles**

- **Separation of concerns:**
    
    - Streamlit = UI
        
    - Backend = processing
        
    - LaTeX = formatting
        
- **LaTeX-first authoring:** keeps academic quality
    
- **JSON communication:** scalable & future-proof
    
- **Tectonic for PDF:** fast, clean, modern
    
- **Modular design:** each lab is a folder
    
- **Future login support baked in**
    

---

## 📌 **What You Already Have**

- Working Streamlit MVP
    
- PDF generation (FPDF prototype)
    
- Proof that multi-student use works
    
- Editable tables, plot generation
    

---

## 📌 **Next Steps for You**

1. Create backend skeleton (FastAPI)
    
2. Write one lab as “template.tex” with placeholders
    
3. Implement LaTeX → HTML endpoint
    
4. Update Streamlit to fetch and display HTML
    
5. Implement PDF generation endpoint
    
6. Connect Streamlit submission to backend PDF
    

