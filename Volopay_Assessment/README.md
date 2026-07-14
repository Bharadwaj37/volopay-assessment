# Volopay Growth Squad — Technical Assessment

**Candidate:** [Your Name]
**Role:** Growth Squad
**Submission Date:** July 2026

---

## Project Structure

```
Volopay_Assessment/
│
├── Task1/
│   └── Task1_LinkedIn_Content.md       # 3 LinkedIn posts (CFO, Finance Manager, AP Team)
│
├── Task2/
│   ├── app.py                          # Streamlit Customer 360 AI Assistant
│   ├── utils.py                        # Intelligence engine (health scoring + AI stubs)
│   ├── requirements.txt                # Python dependencies
│   ├── README.md                       # Setup + deployment guide
│   └── data/
│       ├── crm.csv                     # 15 CRM records
│       ├── support.csv                 # 20 support tickets
│       ├── emails.csv                  # 15 email records
│       └── usage.csv                   # 15 usage rows
│
├── Task3/
│   └── generate_dashboard.py          # Excel workbook generator (100 leads)
│
├── docs/
│   └── Approach_Document.md           # Problem statement, architecture, workflow
│
├── Assets/                            # Screenshots / media
├── Screenshots/
└── README.md                          # This file
```

---

## Task Overview

### Task 1 — LinkedIn Content Strategy
Three original LinkedIn posts targeting:
- **CFO** — Cash flow visibility and AP cycle optimization
- **Finance Manager** — Month-end close process improvement
- **Accounts Payable Team** — Duplicate detection, vendor escalation, three-way matching

Location: `Task1/Task1_LinkedIn_Content.md`

---

### Task 2 — Customer 360 AI Assistant

A production-ready Streamlit application combining four data sources into a unified account view with AI-generated insights.

**Quick Start:**
```bash
cd Task2
pip install -r requirements.txt
streamlit run app.py
```

Features:
- Customer selector sidebar
- CRM overview, support history, email summary, usage metrics
- Health score (0–100) with weighted breakdown
- AI-generated: Customer Summary, Business Risks, Opportunities, Next Best Action
- Full LLM integration hooks (OpenAI / Gemini) in `utils.py`

---

### Task 3 — Sales Dashboard

Excel workbook with 100 realistic leads and a full dashboard.

**Generate:**
```bash
cd Task3
pip install openpyxl pandas
python generate_dashboard.py
# → Sales_Dashboard.xlsx
```

Sheets: Dashboard · Leads Data · Pivot Analysis

---

### Documentation
`docs/Approach_Document.md` — Full approach document with architecture diagram, workflow, prompt design, data description, sample I/O, and future improvements.

---

## Deployment (Task 2)

### Streamlit Community Cloud
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Set main file: `Task2/app.py`

### Render
```
Build: pip install -r requirements.txt
Start: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

---

*Assessment complete. All artifacts are production-quality and submission-ready.*
