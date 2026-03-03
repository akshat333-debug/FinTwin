"""
Government Scheme Recommender for Indian MSMEs.
Rule-based matching of financial health indicators to eligible government schemes.
"""

from __future__ import annotations
from typing import Any


# ── Scheme Database ──────────────────────────────────────────────────────────

SCHEMES = [
    {
        "id": "mudra_shishu",
        "name": "PMMY – Shishu (Mudra Loan)",
        "category": "Credit Access",
        "max_amount": "₹50,000",
        "interest": "~12% p.a.",
        "description": "Collateral-free micro loans for startups and early-stage MSMEs under the Pradhan Mantri Mudra Yojana.",
        "eligibility": "Non-corporate, non-farm small/micro enterprises",
        "url": "https://www.mudra.org.in",
        "icon": "🏦",
    },
    {
        "id": "mudra_kishore",
        "name": "PMMY – Kishore (Mudra Loan)",
        "category": "Credit Access",
        "max_amount": "₹5,00,000",
        "interest": "~12-14% p.a.",
        "description": "Mid-stage MSME financing for businesses that have been operational and need growth capital.",
        "eligibility": "Existing businesses with track record",
        "url": "https://www.mudra.org.in",
        "icon": "🏦",
    },
    {
        "id": "mudra_tarun",
        "name": "PMMY – Tarun (Mudra Loan)",
        "category": "Credit Access",
        "max_amount": "₹10,00,000",
        "interest": "~14-16% p.a.",
        "description": "Higher-value loans for well-established MSMEs looking to scale operations significantly.",
        "eligibility": "Established MSMEs with strong revenue",
        "url": "https://www.mudra.org.in",
        "icon": "🏦",
    },
    {
        "id": "cgtmse",
        "name": "CGTMSE – Credit Guarantee Scheme",
        "category": "Credit Guarantee",
        "max_amount": "₹5 Crore",
        "interest": "Guarantee fee 1-2%",
        "description": "Government-backed credit guarantee that eliminates third-party collateral requirements for MSME loans up to ₹5 Crore.",
        "eligibility": "New and existing micro/small enterprises in manufacturing and services",
        "url": "https://www.cgtmse.in",
        "icon": "🛡️",
    },
    {
        "id": "eclgs",
        "name": "ECLGS – Emergency Credit Line",
        "category": "Emergency Credit",
        "max_amount": "20% of outstanding credit",
        "interest": "9.25% (MSME) / 14% (others)",
        "description": "Emergency working capital facility for businesses impacted by COVID-19, providing additional credit up to 20% of existing outstanding.",
        "eligibility": "MSMEs with existing loans, annual turnover up to ₹500 Crore",
        "url": "https://www.eclgs.com",
        "icon": "🚨",
    },
    {
        "id": "champions",
        "name": "MSME Champions Scheme",
        "category": "Revival Support",
        "max_amount": "₹50 Lakh – ₹25 Crore",
        "interest": "Subsidized rates",
        "description": "Support for manufacturing MSMEs including stressed units. Provides handholding, market linkages, and financial assistance for revival.",
        "eligibility": "Stressed/sick MSMEs in manufacturing sector",
        "url": "https://champions.gov.in",
        "icon": "🏆",
    },
    {
        "id": "stand_up_india",
        "name": "Stand-Up India Scheme",
        "category": "Inclusive Finance",
        "max_amount": "₹10 Lakh – ₹1 Crore",
        "interest": "Base rate + 3% + tenure premium",
        "description": "Bank loans between ₹10 Lakh and ₹1 Crore for SC/ST/Women entrepreneurs for greenfield enterprises.",
        "eligibility": "SC/ST/Women entrepreneurs, greenfield enterprise",
        "url": "https://www.standupmitra.in",
        "icon": "🌱",
    },
    {
        "id": "clcss",
        "name": "CLCSS – Technology Upgradation",
        "category": "Technology",
        "max_amount": "15% subsidy (up to ₹15 Lakh)",
        "interest": "Capital subsidy",
        "description": "15% capital subsidy on institutional finance for technology upgradation of MSMEs, covering plant and machinery.",
        "eligibility": "Existing MSMEs upgrading technology",
        "url": "https://msme.gov.in",
        "icon": "⚙️",
    },
    {
        "id": "pmegp",
        "name": "PMEGP – Employment Generation",
        "category": "Employment",
        "max_amount": "₹25 Lakh (manufacturing) / ₹10 Lakh (services)",
        "interest": "15-35% subsidy",
        "description": "Margin money subsidy for setting up new micro enterprises in rural and urban areas, promoting self-employment.",
        "eligibility": "Individuals above 18, new enterprises only",
        "url": "https://www.kviconline.gov.in/pmegpeportal/",
        "icon": "👥",
    },
    {
        "id": "nsic_raw_material",
        "name": "NSIC – Raw Material Assistance",
        "category": "Working Capital",
        "max_amount": "Based on turnover",
        "interest": "Competitive rates",
        "description": "Financial assistance for procurement of raw materials (indigenous and imported) to MSMEs through NSIC.",
        "eligibility": "Registered MSMEs with Udyam registration",
        "url": "https://www.nsic.co.in",
        "icon": "📦",
    },
    {
        "id": "zed_certification",
        "name": "ZED Certification Scheme",
        "category": "Quality",
        "max_amount": "Up to 80% subsidy on certification cost",
        "interest": "N/A",
        "description": "Zero Defect Zero Effect certification with financial subsidy for quality improvement, testing, and lean manufacturing adoption.",
        "eligibility": "Micro, Small and Medium Enterprises",
        "url": "https://zed.msme.gov.in",
        "icon": "✅",
    },
    {
        "id": "trade_receivables",
        "name": "TReDS – Trade Receivables Platform",
        "category": "Cash Flow",
        "max_amount": "Based on invoices",
        "interest": "Competitive discounting",
        "description": "Electronic platform for financing trade receivables of MSMEs from corporate buyers, reducing payment delays and improving cash flow.",
        "eligibility": "MSMEs with invoices from corporates/PSUs",
        "url": "https://www.rxil.in",
        "icon": "💰",
    },
]


# ── Recommendation Engine ────────────────────────────────────────────────────

def recommend_schemes(
    metrics: dict[str, Any],
    health: dict[str, Any],
    sim_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Recommend government schemes based on financial health indicators.
    Returns a scored + sorted list of scheme recommendations.
    """
    score = health["health_score"]
    grade = health["grade"]
    avg_revenue = metrics.get("avg_revenue", 0)
    avg_profit = metrics.get("avg_monthly_profit", 0)
    cash = metrics.get("latest_cash_reserve", 0)
    burn = metrics.get("burn_rate", 0)
    margin = metrics.get("avg_profit_margin", 0)

    # Calculate cash runway months
    if burn > 0:
        runway_months = cash / burn
    else:
        runway_months = 12  # Profitable, no burn

    # Average survival across all shocks
    avg_survival = sum(s["survival_percentage"] for s in sim_results) / max(len(sim_results), 1)

    recommendations = []

    for scheme in SCHEMES:
        relevance = 0
        reason = ""
        sid = scheme["id"]

        # ── Emergency / Critical health ──
        if sid == "eclgs":
            if score <= 5 or avg_survival < 50:
                relevance = 95
                reason = f"Health score {score}/10 and {avg_survival:.0f}% avg survival — emergency credit line strongly recommended"
            elif score <= 7:
                relevance = 40
                reason = "Moderate stress — emergency credit as precautionary buffer"

        elif sid == "champions":
            if score <= 4:
                relevance = 90
                reason = f"Critical health score ({score}/10) qualifies for MSME revival support"
            elif score <= 6 and avg_survival < 40:
                relevance = 60
                reason = "Below-average health with low survival probability"

        # ── Cash flow / Working capital ──
        elif sid == "trade_receivables":
            if runway_months < 4:
                relevance = 85
                reason = f"Only {runway_months:.1f} months cash runway — TReDS can accelerate receivables"
            elif runway_months < 6:
                relevance = 55
                reason = "Limited cash runway, receivables financing can help"

        elif sid == "nsic_raw_material":
            if margin < 0.15 and avg_revenue > 100000:
                relevance = 70
                reason = f"Thin margins ({margin:.0%}) — raw material assistance can reduce COGS"
            elif margin < 0.25:
                relevance = 35
                reason = "Moderate margins, raw material support beneficial"

        # ── Credit access (Mudra) ──
        elif sid == "mudra_shishu":
            if avg_revenue < 200000:
                relevance = 80
                reason = f"Revenue ₹{avg_revenue/1000:.0f}K/month fits Shishu micro-loan profile"
            elif avg_revenue < 500000:
                relevance = 30
                reason = "Could use Shishu for supplementary working capital"

        elif sid == "mudra_kishore":
            if 200000 <= avg_revenue <= 1000000 and score >= 5:
                relevance = 75
                reason = f"Revenue ₹{avg_revenue/100000:.1f}L qualifies for Kishore growth financing"
            elif avg_revenue <= 500000:
                relevance = 25
                reason = "May qualify for Kishore with growth plan"

        elif sid == "mudra_tarun":
            if avg_revenue > 1000000 and score >= 6:
                relevance = 70
                reason = f"Strong revenue ₹{avg_revenue/100000:.1f}L — Tarun loan for scaling"
            elif avg_revenue > 500000:
                relevance = 30
                reason = "Approaching Tarun eligibility"

        # ── Credit guarantee ──
        elif sid == "cgtmse":
            if score >= 4 and avg_revenue > 100000:
                relevance = 65
                reason = "CGTMSE eliminates collateral requirement for bank loans"
                if score <= 6:
                    relevance = 80
                    reason += f" — especially important at health score {score}/10"

        # ── Growth & quality ──
        elif sid == "stand_up_india":
            if avg_revenue < 500000:
                relevance = 50
                reason = "Suitable for SC/ST/Women entrepreneurs starting greenfield units"

        elif sid == "clcss":
            if score >= 6 and avg_revenue > 300000:
                relevance = 55
                reason = "Healthy business can leverage 15% tech upgrade subsidy"

        elif sid == "pmegp":
            if avg_revenue < 300000:
                relevance = 60
                reason = f"Revenue ₹{avg_revenue/1000:.0f}K — margin money subsidy for growth"

        elif sid == "zed_certification":
            if score >= 7:
                relevance = 45
                reason = "Strong health — ZED certification adds credibility + quality improvement"

        # Only include schemes with relevance > 20
        if relevance > 20:
            recommendations.append({
                **scheme,
                "relevance_score": relevance,
                "reason": reason,
                "urgency": "Critical" if relevance >= 85 else "High" if relevance >= 65 else "Medium" if relevance >= 45 else "Low",
            })

    # Sort by relevance
    recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
    return recommendations
