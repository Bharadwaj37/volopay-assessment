"""
utils.py — Customer 360 AI Assistant
Deterministic rule-based intelligence engine.
Drop-in replacement for LLM-based summaries when no API key is available.
LLM integration points are clearly marked with `# LLM_HOOK` comments.
"""

import pandas as pd
from datetime import datetime, date
from typing import Optional


# ─────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────

def load_crm(path: str = "data/crm.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["renewal_date"])
    df["renewal_date"] = pd.to_datetime(df["renewal_date"])
    return df


def load_support(path: str = "data/support.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["created_date"])
    return df


def load_emails(path: str = "data/emails.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["email_date"])
    return df


def load_usage(path: str = "data/usage.csv") -> Optional[pd.DataFrame]:
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        return None


# ─────────────────────────────────────────────
# CUSTOMER PROFILE BUILDER
# ─────────────────────────────────────────────

def get_customer_profile(customer_id: str,
                          crm_df: pd.DataFrame,
                          support_df: pd.DataFrame,
                          emails_df: pd.DataFrame,
                          usage_df: Optional[pd.DataFrame] = None) -> dict:
    """
    Merges data from all sources into a unified customer profile dict.
    """
    profile = {}

    # CRM
    crm_row = crm_df[crm_df["customer_id"] == customer_id]
    if not crm_row.empty:
        profile["crm"] = crm_row.iloc[0].to_dict()
    else:
        profile["crm"] = {}

    # Support
    tickets = support_df[support_df["customer_id"] == customer_id]
    profile["tickets"] = tickets.to_dict(orient="records")
    profile["open_tickets"] = tickets[tickets["status"] == "Open"].shape[0]
    profile["critical_tickets"] = tickets[tickets["priority"] == "Critical"].shape[0]
    profile["negative_tickets"] = tickets[tickets["sentiment"] == "Negative"].shape[0]

    # Emails
    email_row = emails_df[emails_df["customer_id"] == customer_id]
    if not email_row.empty:
        profile["email"] = email_row.iloc[0].to_dict()
    else:
        profile["email"] = {}

    # Usage (optional)
    if usage_df is not None:
        usage_row = usage_df[usage_df["customer_id"] == customer_id]
        profile["usage"] = usage_row.iloc[0].to_dict() if not usage_row.empty else {}
    else:
        profile["usage"] = {}

    # Days to renewal
    if profile["crm"].get("renewal_date"):
        renewal = pd.to_datetime(profile["crm"]["renewal_date"])
        profile["days_to_renewal"] = (renewal - pd.Timestamp.now()).days
    else:
        profile["days_to_renewal"] = None

    return profile


# ─────────────────────────────────────────────
# HEALTH SCORE ENGINE
# ─────────────────────────────────────────────

def compute_health_score(profile: dict) -> dict:
    """
    Computes a weighted health score (0–100) using deterministic rules.
    Returns score, label, color, and breakdown.
    """
    score = 100
    breakdown = []

    # --- Ticket pressure ---
    critical = profile.get("critical_tickets", 0)
    open_t = profile.get("open_tickets", 0)
    negative = profile.get("negative_tickets", 0)

    if critical > 0:
        deduction = min(critical * 20, 40)
        score -= deduction
        breakdown.append(f"❌ {critical} Critical ticket(s) → -{deduction} pts")
    if open_t > 2:
        deduction = min((open_t - 2) * 5, 20)
        score -= deduction
        breakdown.append(f"⚠️ {open_t} Open tickets → -{deduction} pts")
    if negative > 1:
        deduction = min((negative - 1) * 5, 15)
        score -= deduction
        breakdown.append(f"😟 {negative} Negative sentiment tickets → -{deduction} pts")

    # --- Renewal proximity ---
    days = profile.get("days_to_renewal", 999)
    if days is not None:
        if days < 30:
            score -= 15
            breakdown.append(f"📅 Renewal in {days} days → -15 pts")
        elif days < 60:
            score -= 8
            breakdown.append(f"📅 Renewal in {days} days → -8 pts")

    # --- Usage signals ---
    usage = profile.get("usage", {})
    if usage:
        feature_score = usage.get("feature_adoption_score", 50)
        login_freq = usage.get("login_frequency", "Weekly")
        if feature_score < 40:
            score -= 10
            breakdown.append(f"📉 Low feature adoption ({feature_score}/100) → -10 pts")
        elif feature_score >= 80:
            score += 5
            breakdown.append(f"✅ High feature adoption ({feature_score}/100) → +5 pts")
        if login_freq == "Monthly":
            score -= 10
            breakdown.append("📉 Monthly logins (low engagement) → -10 pts")

    # --- Email sentiment ---
    email_summary = profile.get("email", {}).get("email_summary", "")
    churn_keywords = ["churn", "alternative", "cancel", "patience", "disappointed", "considering"]
    if any(kw in email_summary.lower() for kw in churn_keywords):
        score -= 10
        breakdown.append("📧 Email signals churn risk language → -10 pts")

    score = max(0, min(100, score))

    if score >= 75:
        label = "Healthy"
        color = "#22c55e"
    elif score >= 50:
        label = "At Risk"
        color = "#f59e0b"
    else:
        label = "Critical"
        color = "#ef4444"

    return {"score": score, "label": label, "color": color, "breakdown": breakdown}


# ─────────────────────────────────────────────
# RULE-BASED AI ENGINE
# ─────────────────────────────────────────────

def generate_customer_summary(profile: dict, health: dict) -> str:
    """
    Generates a prose customer summary using deterministic rules.

    # LLM_HOOK: Replace this function body with an OpenAI / Gemini API call.
    # Suggested prompt template below:
    #
    # prompt = f\"\"\"
    # You are a Customer Success Manager AI assistant. Based on the following
    # customer profile data, write a concise 3–4 sentence executive summary
    # that can be used for internal team briefings.
    #
    # Customer: {profile['crm']['company']}
    # Plan: {profile['crm']['plan']} | ARR: ${profile['crm']['ARR']:,}
    # Days to Renewal: {profile['days_to_renewal']}
    # Open Tickets: {profile['open_tickets']} | Critical: {profile['critical_tickets']}
    # Health Score: {health['score']}/100 ({health['label']})
    # Email Summary: {profile['email'].get('email_summary', 'N/A')}
    # Usage (Feature Adoption): {profile['usage'].get('feature_adoption_score', 'N/A')}
    # \"\"\"
    """
    crm = profile.get("crm", {})
    company = crm.get("company", "This customer")
    plan = crm.get("plan", "Unknown")
    arr = crm.get("ARR", 0)
    owner = crm.get("owner", "Unassigned")
    days = profile.get("days_to_renewal", "Unknown")
    open_t = profile.get("open_tickets", 0)
    critical = profile.get("critical_tickets", 0)
    score = health["score"]
    label = health["label"]
    email_summary = profile.get("email", {}).get("email_summary", "")

    lines = []
    lines.append(
        f"**{company}** is on the **{plan}** plan with an ARR of **${arr:,}**, "
        f"managed by **{owner}**."
    )

    if isinstance(days, int):
        if days < 60:
            lines.append(
                f"Their renewal is in **{days} days**, making this an urgent account to prioritize."
            )
        else:
            lines.append(f"Their renewal is in **{days} days** — standard timeline.")

    if critical > 0:
        lines.append(
            f"There are **{critical} critical support ticket(s)** currently open, "
            f"which presents an escalation risk and requires immediate CSM attention."
        )
    elif open_t > 0:
        lines.append(
            f"The account has **{open_t} open support ticket(s)**, with no critical blockers currently."
        )
    else:
        lines.append("There are no open support tickets — the account is operationally stable.")

    if email_summary:
        lines.append(f"Latest email signal: *{email_summary[:200]}*")

    lines.append(
        f"Overall account health is rated **{label}** ({score}/100) based on support load, "
        f"renewal proximity, and usage signals."
    )

    return "\n\n".join(lines)


def generate_business_risks(profile: dict, health: dict) -> list:
    """
    Returns a list of business risk strings.

    # LLM_HOOK: Replace with LLM call to generate nuanced, context-aware risks.
    """
    risks = []
    crm = profile.get("crm", {})
    arr = crm.get("ARR", 0)
    days = profile.get("days_to_renewal", 999)
    critical = profile.get("critical_tickets", 0)
    open_t = profile.get("open_tickets", 0)
    email_summary = profile.get("email", {}).get("email_summary", "")
    usage = profile.get("usage", {})

    if critical > 0:
        risks.append(
            f"🚨 **Critical Support Escalation**: {critical} critical ticket(s) unresolved. "
            f"At ARR of ${arr:,}, this is a high-value churn risk."
        )

    churn_keywords = ["churn", "alternative", "cancel", "patience", "disappointed", "considering"]
    if any(kw in email_summary.lower() for kw in churn_keywords):
        risks.append(
            "⚠️ **Churn Language Detected**: Recent email communication contains signals "
            "indicating the customer is evaluating alternatives."
        )

    if isinstance(days, int) and days < 60:
        risks.append(
            f"📅 **Renewal at Risk**: Only {days} days to renewal with unresolved issues. "
            f"High probability of downsell or non-renewal without intervention."
        )

    if open_t > 3:
        risks.append(
            f"🎫 **Support Overload**: {open_t} open tickets suggests the customer "
            f"is struggling operationally, increasing churn risk."
        )

    if usage:
        feature_score = usage.get("feature_adoption_score", 100)
        if feature_score < 45:
            risks.append(
                f"📉 **Low Product Adoption**: Feature adoption score of {feature_score}/100. "
                f"Customer may not be realizing full product value, weakening renewal justification."
            )

    if not risks:
        risks.append("✅ No critical business risks identified at this time.")

    return risks


def generate_business_opportunities(profile: dict, health: dict) -> list:
    """
    Returns a list of business opportunity strings.

    # LLM_HOOK: Replace with LLM call for contextual upsell/expansion recommendations.
    """
    opportunities = []
    crm = profile.get("crm", {})
    plan = crm.get("plan", "")
    arr = crm.get("ARR", 0)
    usage = profile.get("usage", {})
    email_summary = profile.get("email", {}).get("email_summary", "")
    days = profile.get("days_to_renewal", 999)

    if plan == "Starter" and arr >= 12000:
        opportunities.append(
            "📈 **Upsell to Growth Plan**: Customer is on Starter but showing strong usage. "
            "A Growth plan migration could unlock automation features and increase ARR."
        )

    if plan == "Growth":
        opportunities.append(
            "🚀 **Enterprise Upgrade Potential**: Growth plan customers with positive usage "
            "metrics are strong candidates for Enterprise, which offers dedicated CSM and API access."
        )

    if usage:
        api_calls = usage.get("api_calls", 0)
        feature_score = usage.get("feature_adoption_score", 0)
        if api_calls > 10000:
            opportunities.append(
                f"🔗 **API Power User**: {api_calls:,} API calls this month. "
                f"This customer is a strong candidate for advanced integrations or a technical partnership program."
            )
        if feature_score >= 85:
            opportunities.append(
                "🏆 **Reference / Case Study Candidate**: High feature adoption and positive engagement "
                "makes this customer a strong candidate for a testimonial or co-marketing opportunity."
            )

    upgrade_keywords = ["upgrade", "more users", "expand", "new team", "additional"]
    if any(kw in email_summary.lower() for kw in upgrade_keywords):
        opportunities.append(
            "💡 **Expansion Intent Detected**: Recent email indicates the customer may be open "
            "to expanding their usage or user seats."
        )

    renewal_keywords = ["renewal", "schedule a call", "upgrade", "happy", "helpful"]
    if any(kw in email_summary.lower() for kw in renewal_keywords):
        opportunities.append(
            "📞 **Renewal Discussion Ready**: Customer email tone suggests openness to renewal "
            "conversation. Ideal time to schedule a QBR."
        )

    if not opportunities:
        opportunities.append("💬 Schedule a QBR to surface expansion and adoption opportunities.")

    return opportunities


def generate_next_best_action(profile: dict, health: dict, risks: list, opportunities: list) -> dict:
    """
    Returns the single most important next action with context.

    # LLM_HOOK: Replace with LLM call for intelligent, prioritized action generation.
    """
    crm = profile.get("crm", {})
    critical = profile.get("critical_tickets", 0)
    open_t = profile.get("open_tickets", 0)
    days = profile.get("days_to_renewal", 999)
    score = health["score"]
    owner = crm.get("owner", "CSM")
    company = crm.get("company", "the customer")
    arr = crm.get("ARR", 0)

    if critical > 0:
        return {
            "action": f"Escalate {critical} critical ticket(s) to Engineering with VP-level visibility",
            "why": (
                f"{company} has {critical} critical unresolved ticket(s). "
                f"At ARR of ${arr:,}, unresolved critical issues are the #1 predictor of churn. "
                f"Loop in engineering lead and schedule a customer call within 24 hours."
            ),
            "owner": owner,
            "urgency": "🔴 Immediate (< 24 hrs)",
            "icon": "🚨"
        }

    if score < 50 and isinstance(days, int) and days < 90:
        return {
            "action": "Schedule an Executive Business Review (EBR) with decision-maker",
            "why": (
                f"Health score is {score}/100 with renewal in {days} days. "
                f"An EBR with the CFO or Finance VP at {company} is the most effective intervention "
                f"to align on value and secure renewal."
            ),
            "owner": owner,
            "urgency": "🟠 High (< 1 week)",
            "icon": "📊"
        }

    if open_t > 2:
        return {
            "action": f"Conduct a proactive support review call with {company}",
            "why": (
                f"{open_t} open tickets suggests friction in their operations. "
                f"A structured support review call with their operations lead can reduce "
                f"ticket backlog, demonstrate care, and uncover deeper product gaps."
            ),
            "owner": owner,
            "urgency": "🟡 Medium (< 3 days)",
            "icon": "🎫"
        }

    if isinstance(days, int) and days < 60:
        return {
            "action": f"Initiate renewal conversation with {company}",
            "why": (
                f"Renewal is {days} days away. Health score is {score}/100. "
                f"Start the renewal conversation now to allow time for negotiation, "
                f"contract review, and any required approvals on the customer side."
            ),
            "owner": owner,
            "urgency": "🟡 Medium (< 1 week)",
            "icon": "📅"
        }

    return {
        "action": f"Schedule a quarterly check-in and explore expansion with {company}",
        "why": (
            f"Account health is strong ({score}/100). No immediate risks. "
            f"This is the right time to run a QBR, reinforce product value, "
            f"and explore Growth or Enterprise upgrade opportunities."
        ),
        "owner": owner,
        "urgency": "🟢 Low (< 2 weeks)",
        "icon": "📞"
    }


# ─────────────────────────────────────────────
# LLM INTEGRATION STUBS
# ─────────────────────────────────────────────

def call_openai(prompt: str, api_key: str) -> str:
    """
    LLM_HOOK: Call OpenAI GPT-4 to generate customer insights.
    Uncomment and install `openai` package to activate.
    """
    # from openai import OpenAI
    # client = OpenAI(api_key=api_key)
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[{"role": "user", "content": prompt}],
    #     temperature=0.3,
    # )
    # return response.choices[0].message.content
    raise NotImplementedError("OpenAI LLM hook not yet activated.")


def call_gemini(prompt: str, api_key: str) -> str:
    """
    LLM_HOOK: Call Google Gemini to generate customer insights.
    Uncomment and install `google-generativeai` package to activate.
    """
    # import google.generativeai as genai
    # genai.configure(api_key=api_key)
    # model = genai.GenerativeModel("gemini-1.5-pro")
    # response = model.generate_content(prompt)
    # return response.text
    raise NotImplementedError("Gemini LLM hook not yet activated.")
