"""
app.py — Customer 360 AI Assistant
Growth Squad Assessment | Volopay
"""

import os
import streamlit as st
import pandas as pd
from datetime import datetime
from utils import (
    load_crm, load_support, load_emails, load_usage,
    get_customer_profile, compute_health_score,
    generate_customer_summary, generate_business_risks,
    generate_business_opportunities, generate_next_best_action,
)

# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Customer 360 | AI Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background: #0f1117; }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e2130 0%, #252836 100%);
        border: 1px solid #2d3148;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
    }
    .metric-card h4 { color: #a0aec0; font-size: 12px; font-weight: 600;
                       letter-spacing: 1px; text-transform: uppercase; margin: 0 0 8px 0; }
    .metric-card .value { color: #ffffff; font-size: 24px; font-weight: 700; margin: 0; }
    .metric-card .sub { color: #718096; font-size: 12px; margin-top: 4px; }

    /* Section headers */
    .section-header {
        background: linear-gradient(135deg, #1a1f35 0%, #1e2440 100%);
        border-left: 4px solid #6366f1;
        border-radius: 0 8px 8px 0;
        padding: 12px 18px;
        margin: 20px 0 12px 0;
    }
    .section-header h3 { color: #e2e8f0; margin: 0; font-size: 16px; font-weight: 600; }

    /* Health badge */
    .health-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        letter-spacing: 0.5px;
    }

    /* Risk / opportunity cards */
    .risk-card {
        background: #1a1015;
        border: 1px solid #7f1d1d;
        border-radius: 10px;
        padding: 14px 16px;
        margin: 8px 0;
        color: #fca5a5;
        font-size: 14px;
        line-height: 1.6;
    }
    .opp-card {
        background: #0d1f1a;
        border: 1px solid #166534;
        border-radius: 10px;
        padding: 14px 16px;
        margin: 8px 0;
        color: #86efac;
        font-size: 14px;
        line-height: 1.6;
    }
    .nba-card {
        background: linear-gradient(135deg, #1e1a40 0%, #252050 100%);
        border: 1px solid #6366f1;
        border-radius: 14px;
        padding: 24px;
        margin: 12px 0;
    }
    .nba-card .action { color: #a5b4fc; font-size: 20px; font-weight: 700; margin-bottom: 12px; }
    .nba-card .why { color: #c7d2fe; font-size: 14px; line-height: 1.7; }
    .nba-card .meta { color: #7c85b0; font-size: 12px; margin-top: 14px; }

    /* Ticket table */
    .ticket-row {
        background: #1a1f2e;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 6px 0;
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 13px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #111827 100%);
        border-right: 1px solid #1f2937;
    }
    [data-testid="stSidebar"] h1 { color: #ffffff; }

    /* Hide streamlit watermark */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Dividers */
    hr { border-color: #1f2937; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOAD DATA (cached)
# ─────────────────────────────────────────────
@st.cache_data
def load_all_data():
    base = os.path.join(os.path.dirname(__file__), "data")
    crm_df = load_crm(os.path.join(base, "crm.csv"))
    support_df = load_support(os.path.join(base, "support.csv"))
    emails_df = load_emails(os.path.join(base, "emails.csv"))
    usage_df = load_usage(os.path.join(base, "usage.csv"))
    return crm_df, support_df, emails_df, usage_df


crm_df, support_df, emails_df, usage_df = load_all_data()


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
PRIORITY_COLOR = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
STATUS_COLOR = {"Open": "#ef4444", "In Progress": "#f59e0b", "Resolved": "#22c55e"}
PLAN_COLOR = {"Starter": "#60a5fa", "Growth": "#a78bfa", "Enterprise": "#fbbf24"}


def fmt_arr(val):
    if val >= 1_000_000:
        return f"${val/1_000_000:.1f}M"
    elif val >= 1_000:
        return f"${val/1_000:.0f}K"
    return f"${val:,}"


def days_color(days):
    if days < 30:
        return "#ef4444"
    if days < 60:
        return "#f59e0b"
    return "#22c55e"


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 Customer 360")
    st.markdown("**AI-Powered Account Intelligence**")
    st.markdown("---")

    customer_options = {
        f"{row['company']} ({row['customer_id']})": row["customer_id"]
        for _, row in crm_df.iterrows()
    }
    selected_label = st.selectbox(
        "Select Account",
        list(customer_options.keys()),
        key="customer_selector"
    )
    selected_id = customer_options[selected_label]

    st.markdown("---")
    st.markdown("### ⚙️ AI Mode")
    ai_mode = st.radio(
        "Insight Engine",
        ["🤖 Rule-Based (Active)", "🔑 OpenAI GPT-4", "🌟 Google Gemini"],
        index=0,
        help="Rule-Based is fully functional without an API key."
    )
    if ai_mode != "🤖 Rule-Based (Active)":
        api_key = st.text_input("API Key", type="password", placeholder="sk-... or AIza...")
        st.caption("⚠️ API integration stub is ready. See `utils.py` → `call_openai()` / `call_gemini()`")
    else:
        api_key = None
        st.caption("✅ Running deterministic rule engine. No API key required.")

    st.markdown("---")
    st.markdown("### 📊 Portfolio Snapshot")
    total_arr = crm_df["ARR"].sum()
    st.metric("Total ARR", fmt_arr(total_arr))
    st.metric("Active Accounts", len(crm_df))
    open_tickets_total = support_df[support_df["status"] == "Open"].shape[0]
    st.metric("Open Tickets", open_tickets_total)

    st.markdown("---")
    st.caption("Customer 360 AI | Growth Squad Assessment")
    st.caption("Built with Streamlit + Pandas")


# ─────────────────────────────────────────────
# BUILD PROFILE
# ─────────────────────────────────────────────
profile = get_customer_profile(selected_id, crm_df, support_df, emails_df, usage_df)
health = compute_health_score(profile)

crm = profile["crm"]
company = crm.get("company", "Unknown")
plan = crm.get("plan", "—")
arr = crm.get("ARR", 0)
owner = crm.get("owner", "—")
days = profile.get("days_to_renewal")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown(f"# 🏢 {company}")
    st.markdown(f"Customer ID: `{selected_id}` &nbsp;&nbsp; Owner: **{owner}**")
with col_badge:
    badge_color = health["color"]
    badge_label = health["label"]
    score = health["score"]
    st.markdown(f"""
    <div style='text-align:right; padding-top:16px;'>
        <div style='background:{badge_color}22; border:2px solid {badge_color}; 
                    border-radius:12px; padding:12px 20px; display:inline-block;'>
            <div style='color:{badge_color}; font-size:28px; font-weight:800;'>{score}/100</div>
            <div style='color:{badge_color}; font-size:13px; font-weight:600; letter-spacing:1px;'>{badge_label.upper()}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 1 — CRM OVERVIEW
# ─────────────────────────────────────────────
st.markdown("""<div class="section-header"><h3>📋 CRM Overview</h3></div>""", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
plan_color = PLAN_COLOR.get(plan, "#94a3b8")

with c1:
    st.markdown(f"""<div class="metric-card">
        <h4>Plan</h4>
        <p class="value" style="color:{plan_color};">{plan}</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
        <h4>ARR</h4>
        <p class="value">{fmt_arr(arr)}</p>
    </div>""", unsafe_allow_html=True)
with c3:
    renewal_str = pd.to_datetime(crm.get("renewal_date")).strftime("%d %b %Y") if crm.get("renewal_date") else "—"
    d_color = days_color(days) if isinstance(days, int) else "#94a3b8"
    st.markdown(f"""<div class="metric-card">
        <h4>Renewal Date</h4>
        <p class="value" style="color:{d_color};">{renewal_str}</p>
        <p class="sub">{days} days remaining</p>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card">
        <h4>Account Owner</h4>
        <p class="value" style="font-size:18px;">{owner}</p>
    </div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""<div class="metric-card">
        <h4>Customer ID</h4>
        <p class="value" style="font-size:18px;">{selected_id}</p>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECTION 2 — SUPPORT HISTORY
# ─────────────────────────────────────────────
st.markdown("""<div class="section-header"><h3>🎫 Support History</h3></div>""", unsafe_allow_html=True)

tickets = profile.get("tickets", [])
if tickets:
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""<div class="metric-card">
            <h4>Total Tickets</h4>
            <p class="value">{len(tickets)}</p>
        </div>""", unsafe_allow_html=True)
    with s2:
        open_count = profile["open_tickets"]
        st.markdown(f"""<div class="metric-card">
            <h4>Open</h4>
            <p class="value" style="color:#ef4444;">{open_count}</p>
        </div>""", unsafe_allow_html=True)
    with s3:
        crit_count = profile["critical_tickets"]
        st.markdown(f"""<div class="metric-card">
            <h4>Critical</h4>
            <p class="value" style="color:#dc2626;">{crit_count}</p>
        </div>""", unsafe_allow_html=True)
    with s4:
        neg_count = profile["negative_tickets"]
        st.markdown(f"""<div class="metric-card">
            <h4>Negative Sentiment</h4>
            <p class="value" style="color:#f59e0b;">{neg_count}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tickets_df = pd.DataFrame(tickets)
    display_cols = ["ticket_id", "ticket", "priority", "status", "sentiment", "created_date"]
    existing_cols = [c for c in display_cols if c in tickets_df.columns]

    # Apply color styling
    def style_priority(val):
        colors = {"Critical": "#dc2626", "High": "#f59e0b", "Medium": "#3b82f6", "Low": "#22c55e"}
        c = colors.get(val, "#94a3b8")
        return f"color: {c}; font-weight: 600;"

    def style_status(val):
        colors = {"Open": "#ef4444", "In Progress": "#f59e0b", "Resolved": "#22c55e"}
        c = colors.get(val, "#94a3b8")
        return f"color: {c}; font-weight: 600;"

    styled_df = tickets_df[existing_cols].style.map(
        style_priority, subset=["priority"]
    ).map(
        style_status, subset=["status"]
    )
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
else:
    st.info("No support tickets found for this account.")

# ─────────────────────────────────────────────
# SECTION 3 — EMAIL SUMMARY
# ─────────────────────────────────────────────
st.markdown("""<div class="section-header"><h3>📧 Latest Email Communication</h3></div>""", unsafe_allow_html=True)

email = profile.get("email", {})
if email:
    em1, em2 = st.columns([2, 3])
    with em1:
        st.markdown(f"""<div class="metric-card">
            <h4>Date</h4><p class="value" style="font-size:16px;">{pd.to_datetime(email.get('email_date')).strftime('%d %b %Y') if email.get('email_date') else '—'}</p>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="metric-card">
            <h4>Sender</h4><p class="value" style="font-size:14px;">{email.get('sender','—')}</p>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="metric-card">
            <h4>Subject</h4><p class="value" style="font-size:14px;">{email.get('subject','—')}</p>
        </div>""", unsafe_allow_html=True)
    with em2:
        st.markdown("""<div style='background:#1a1f2e; border-radius:12px; padding:20px; margin-top:8px;'>
            <p style='color:#a0aec0; font-size:12px; font-weight:600; letter-spacing:1px; 
                       text-transform:uppercase; margin-bottom:10px;'>Email Body</p>""",
            unsafe_allow_html=True)
        st.write(email.get("latest_email", "No email content available."))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""<div style='background:#0d1f1a; border:1px solid #166534; border-radius:10px; 
                                   padding:14px; margin-top:12px;'>
            <p style='color:#6ee7b7; font-size:12px; font-weight:600; 
                      text-transform:uppercase; margin-bottom:8px;'>🤖 AI Email Summary</p>""",
            unsafe_allow_html=True)
        st.write(email.get("email_summary", "No summary available."))
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("No email records found for this account.")

# ─────────────────────────────────────────────
# SECTION 4 — USAGE (if available)
# ─────────────────────────────────────────────
usage = profile.get("usage", {})
if usage:
    st.markdown("""<div class="section-header"><h3>📈 Product Usage</h3></div>""", unsafe_allow_html=True)
    u1, u2, u3, u4, u5 = st.columns(5)
    with u1:
        st.markdown(f"""<div class="metric-card">
            <h4>Invoices Processed</h4>
            <p class="value">{usage.get('invoices_processed', '—'):,}</p>
        </div>""", unsafe_allow_html=True)
    with u2:
        st.markdown(f"""<div class="metric-card">
            <h4>Payments Made</h4>
            <p class="value">{usage.get('payments_made', '—'):,}</p>
        </div>""", unsafe_allow_html=True)
    with u3:
        st.markdown(f"""<div class="metric-card">
            <h4>Active Users</h4>
            <p class="value">{usage.get('active_users', '—')}</p>
        </div>""", unsafe_allow_html=True)
    with u4:
        st.markdown(f"""<div class="metric-card">
            <h4>API Calls</h4>
            <p class="value">{usage.get('api_calls', '—'):,}</p>
        </div>""", unsafe_allow_html=True)
    with u5:
        fa_score = usage.get('feature_adoption_score', 0)
        fa_color = "#22c55e" if fa_score >= 70 else "#f59e0b" if fa_score >= 45 else "#ef4444"
        st.markdown(f"""<div class="metric-card">
            <h4>Adoption Score</h4>
            <p class="value" style="color:{fa_color};">{fa_score}/100</p>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECTION 5 — AI INSIGHTS
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("## 🤖 AI-Generated Customer Intelligence")
st.caption(
    "Running on deterministic rule engine. "
    "Replace with OpenAI/Gemini by setting API key in sidebar and activating hooks in `utils.py`."
)

tab_summary, tab_risks, tab_opps, tab_nba, tab_health = st.tabs([
    "📝 Customer Summary",
    "⚠️ Business Risks",
    "💡 Opportunities",
    "🎯 Next Best Action",
    "🏥 Health Breakdown",
])

with tab_summary:
    summary = generate_customer_summary(profile, health)
    st.markdown(
        f"""<div style='background:#1a1f2e; border-radius:12px; padding:24px; 
                        line-height:1.8; color:#e2e8f0; font-size:15px;'>
        {summary}
        </div>""",
        unsafe_allow_html=True
    )

with tab_risks:
    risks = generate_business_risks(profile, health)
    for risk in risks:
        st.markdown(f'<div class="risk-card">{risk}</div>', unsafe_allow_html=True)

with tab_opps:
    opportunities = generate_business_opportunities(profile, health)
    for opp in opportunities:
        st.markdown(f'<div class="opp-card">{opp}</div>', unsafe_allow_html=True)

with tab_nba:
    risks_list = generate_business_risks(profile, health)
    opps_list = generate_business_opportunities(profile, health)
    nba = generate_next_best_action(profile, health, risks_list, opps_list)
    st.markdown(f"""
    <div class="nba-card">
        <div style="font-size:40px; margin-bottom:8px;">{nba['icon']}</div>
        <div class="action">{nba['action']}</div>
        <div class="why">{nba['why']}</div>
        <div class="meta">
            👤 Owner: <strong style="color:#a5b4fc;">{nba['owner']}</strong> &nbsp;|&nbsp;
            ⏱️ Urgency: <strong>{nba['urgency']}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab_health:
    hcol1, hcol2 = st.columns([1, 2])
    with hcol1:
        h_color = health["color"]
        h_score = health["score"]
        h_label = health["label"]
        st.markdown(f"""
        <div style='text-align:center; padding:40px 0;'>
            <div style='font-size:72px; font-weight:800; color:{h_color};'>{h_score}</div>
            <div style='font-size:16px; color:{h_color}; font-weight:600; letter-spacing:2px;'>
                {h_label.upper()}
            </div>
            <div style='color:#718096; font-size:13px; margin-top:8px;'>Health Score (out of 100)</div>
        </div>
        """, unsafe_allow_html=True)
    with hcol2:
        st.markdown("**Score Breakdown:**")
        breakdown = health.get("breakdown", [])
        if breakdown:
            for item in breakdown:
                st.markdown(f"- {item}")
        else:
            st.success("✅ No deductions — account is in excellent health!")
