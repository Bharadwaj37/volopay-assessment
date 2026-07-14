# Customer 360 AI Assistant

> **Growth Squad Technical Assessment | Volopay**

A production-ready Streamlit application that unifies customer data from CRM, support, email, and usage sources into a single intelligent account view — with built-in AI-generated insights, health scoring, and next best action recommendations.

---

## Features

| Feature | Description |
|---|---|
| **Customer Selector** | Sidebar dropdown to switch between all accounts instantly |
| **CRM Overview** | Plan, ARR, renewal date, owner — all in one glance |
| **Support History** | All tickets with priority, status, and sentiment coloring |
| **Email Summary** | Latest email body + AI-generated summary |
| **Usage Metrics** | Invoices, payments, active users, API calls, adoption score |
| **Health Score** | Weighted 0–100 score with transparent breakdown |
| **AI Summary** | Auto-generated executive summary per account |
| **Business Risks** | Rule-based risk detection with churn signals |
| **Opportunities** | Upsell, expansion, and advocacy opportunities |
| **Next Best Action** | Single highest-priority action with owner and urgency |

---

## Project Structure

```
Task2/
├── app.py                 # Main Streamlit application
├── utils.py               # Data loaders, health engine, AI insight engine
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── data/
    ├── crm.csv            # CRM records (15 accounts)
    ├── support.csv        # Support tickets (20 tickets)
    ├── emails.csv         # Latest email per account
    └── usage.csv          # Monthly product usage metrics
```

---

## Running Locally

```bash
# 1. Clone / navigate to the Task2 directory
cd Volopay_Assessment/Task2

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## AI Mode

The app ships with a fully functional **deterministic rule-based engine** that requires no API key.

To activate LLM-powered insights:

1. Open `utils.py`
2. Locate the `# LLM_HOOK` comments
3. Uncomment the relevant code block (`call_openai` or `call_gemini`)
4. Add your API key in the sidebar

---

## Deployment

### Streamlit Community Cloud

1. Push this directory to a public GitHub repository
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select the repo, set branch to `main`, set main file to `Task2/app.py`
5. Click **Deploy**

> Set any secret API keys via **Manage App → Secrets** in the Streamlit Cloud dashboard.

### Render

1. Create a new **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repository
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Add environment variables for API keys if needed

---

## Data Sources

| File | Records | Key Fields |
|---|---|---|
| `crm.csv` | 15 customers | customer_id, company, plan, ARR, renewal_date |
| `support.csv` | 20 tickets | ticket_id, priority, status, sentiment |
| `emails.csv` | 15 emails | subject, latest_email, email_summary |
| `usage.csv` | 15 usage rows | invoices_processed, api_calls, feature_adoption_score |

---

## Health Score Logic

| Signal | Weight |
|---|---|
| Critical tickets | -20 pts each (max -40) |
| Open ticket count > 2 | -5 pts each (max -20) |
| Negative sentiment tickets > 1 | -5 pts each (max -15) |
| Renewal < 30 days | -15 pts |
| Renewal 30–60 days | -8 pts |
| Low feature adoption (< 40) | -10 pts |
| Monthly login frequency | -10 pts |
| Churn language in emails | -10 pts |
| High adoption (> 80) | +5 pts |

---

*Built for the Volopay Growth Squad Assessment | July 2026*
