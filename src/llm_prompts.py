"""
LLM Prompt Templates for Risk Summary and Financial Roadmap.

Tasks 9 & 10: Generates structured prompts that can be sent to any LLM
(OpenAI, local LLM, etc.) for:
  - Top 3 risk explanations
  - 5 prioritized financial action items

No LLM is called directly here — these are pure template functions
that output prompt strings + a simple mock/wrapper for development.
"""

from __future__ import annotations

import json
from typing import Any


# ---------------------------------------------------------------------------
# Task 9: Risk Summary Prompt
# ---------------------------------------------------------------------------

RISK_SUMMARY_TEMPLATE = """You are an expert Indian MSME financial advisor.

Analyze the following financial data and simulation results for a small business.
Identify the TOP 3 risks this business faces, ranked by severity.

## Business Financial Summary
- Average Monthly Revenue: ₹{avg_revenue:,.0f}
- Average Monthly Profit: ₹{avg_monthly_profit:,.0f}
- Profit Margin: {avg_profit_margin:.1%}
- Revenue Volatility: {revenue_volatility:.2%}
- Cash Reserve: ₹{latest_cash_reserve:,.0f}
- Burn Rate: ₹{burn_rate:,.0f}/month (during loss months)
- Fixed Cost Ratio: {fixed_cost_ratio:.1%}
- Health Score: {health_score}/10 ({grade})
- Months of Data: {months_of_data}

## Stress Test Results
{simulation_summary}

## Instructions
For each risk, provide:
1. **Risk Name** — a concise label
2. **Severity** — Critical / High / Medium / Low
3. **Explanation** — 2-3 sentences explaining the risk in context of this business
4. **Evidence** — specific metric values that support this risk assessment

Respond ONLY in valid JSON format:
```json
[
  {{
    "risk_name": "...",
    "severity": "...",
    "explanation": "...",
    "evidence": "..."
  }}
]
```
"""


def build_risk_prompt(
    metrics: dict[str, Any],
    health_result: dict[str, Any],
    simulation_results: list[dict[str, Any]],
) -> str:
    """Build a prompt for LLM risk summary generation.

    Parameters
    ----------
    metrics : dict
        Output of compute_metrics().
    health_result : dict
        Output of calculate_health_score().
    simulation_results : list[dict]
        Output of run_all_simulations().

    Returns
    -------
    str
        Formatted prompt string ready for LLM consumption.
    """
    sim_lines = []
    for r in simulation_results:
        sim_lines.append(
            f"- {r['shock_name']}: {r['survival_percentage']:.1f}% survival "
            f"({r['survived_count']}/{r['n_simulations']} simulations)"
        )
    simulation_summary = "\n".join(sim_lines)

    return RISK_SUMMARY_TEMPLATE.format(
        avg_revenue=metrics["avg_revenue"],
        avg_monthly_profit=metrics["avg_monthly_profit"],
        avg_profit_margin=metrics["avg_profit_margin"],
        revenue_volatility=metrics["revenue_volatility"],
        latest_cash_reserve=metrics["latest_cash_reserve"],
        burn_rate=metrics["burn_rate"],
        fixed_cost_ratio=metrics["fixed_cost_ratio"],
        health_score=health_result["health_score"],
        grade=health_result["grade"],
        months_of_data=metrics["months_of_data"],
        simulation_summary=simulation_summary,
    )


# ---------------------------------------------------------------------------
# Task 10: Financial Roadmap Prompt
# ---------------------------------------------------------------------------

ROADMAP_TEMPLATE = """You are an expert Indian MSME financial advisor.

Based on the following financial analysis, generate exactly 5 PRIORITIZED action items
that this business should take to improve its financial resilience.

## Business Financial Summary
- Average Monthly Revenue: ₹{avg_revenue:,.0f}
- Average Monthly Profit: ₹{avg_monthly_profit:,.0f}
- Profit Margin: {avg_profit_margin:.1%}
- Revenue Volatility: {revenue_volatility:.2%}
- Cash Reserve: ₹{latest_cash_reserve:,.0f}
- Burn Rate: ₹{burn_rate:,.0f}/month
- Fixed Cost Ratio: {fixed_cost_ratio:.1%}
- Health Score: {health_score}/10 ({grade})

## Top Risks Identified
{risk_summary}

## Weakest Stress Scenarios
{weakest_scenarios}

## Instructions
Generate exactly 5 actions. For each action, provide:
1. **action** — clear, specific, actionable recommendation
2. **impact** — expected financial impact (quantify if possible)
3. **timeline** — implementation timeline (e.g., "1-2 weeks", "1 month")
4. **priority** — 1 (highest) to 5 (lowest)
5. **category** — one of: Cost Reduction, Revenue Growth, Cash Management, Risk Mitigation, Operational Efficiency

Actions MUST be tied to the simulation results and financial data above.
Actions MUST be practical for an Indian MSME (₹5L-50L monthly revenue range).

Respond ONLY in valid JSON format:
```json
[
  {{
    "action": "...",
    "impact": "...",
    "timeline": "...",
    "priority": 1,
    "category": "..."
  }}
]
```
"""


def build_roadmap_prompt(
    metrics: dict[str, Any],
    health_result: dict[str, Any],
    simulation_results: list[dict[str, Any]],
    risk_analysis: list[dict[str, Any]] | None = None,
) -> str:
    """Build a prompt for LLM roadmap generation.

    Parameters
    ----------
    metrics : dict
        Output of compute_metrics().
    health_result : dict
        Output of calculate_health_score().
    simulation_results : list[dict]
        Output of run_all_simulations().
    risk_analysis : list[dict] | None
        Parsed risk output from LLM (if available).

    Returns
    -------
    str
        Formatted prompt string.
    """
    # Risk summary
    if risk_analysis:
        risk_lines = [
            f"- [{r.get('severity', 'N/A')}] {r.get('risk_name', 'Unknown')}: "
            f"{r.get('explanation', 'N/A')}"
            for r in risk_analysis
        ]
    else:
        risk_lines = ["- Risk analysis not yet available"]
    risk_summary = "\n".join(risk_lines)

    # Find 3 weakest scenarios
    sorted_sims = sorted(simulation_results, key=lambda x: x["survival_probability"])
    weakest = sorted_sims[:3]
    weak_lines = [
        f"- {w['shock_name']}: {w['survival_percentage']:.1f}% survival"
        for w in weakest
    ]
    weakest_scenarios = "\n".join(weak_lines)

    return ROADMAP_TEMPLATE.format(
        avg_revenue=metrics["avg_revenue"],
        avg_monthly_profit=metrics["avg_monthly_profit"],
        avg_profit_margin=metrics["avg_profit_margin"],
        revenue_volatility=metrics["revenue_volatility"],
        latest_cash_reserve=metrics["latest_cash_reserve"],
        burn_rate=metrics["burn_rate"],
        fixed_cost_ratio=metrics["fixed_cost_ratio"],
        health_score=health_result["health_score"],
        grade=health_result["grade"],
        risk_summary=risk_summary,
        weakest_scenarios=weakest_scenarios,
    )


# ---------------------------------------------------------------------------
# Mock LLM Wrapper (for development without API key)
# ---------------------------------------------------------------------------


def generate_mock_risks(
    metrics: dict[str, Any],
    simulation_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate deterministic mock risk analysis (no LLM needed).

    Used for development, testing, and environments without an LLM API key.
    """
    risks = []

    # Sort simulations by survival probability (lowest first)
    sorted_sims = sorted(simulation_results, key=lambda x: x["survival_probability"])

    # Risk 1: Worst shock scenario
    worst = sorted_sims[0]
    risks.append({
        "risk_name": f"{worst['shock_name']} Vulnerability",
        "severity": "Critical" if worst["survival_percentage"] < 50 else "High",
        "explanation": (
            f"Under a {worst['shock_name'].lower()} scenario, the business has only "
            f"{worst['survival_percentage']:.0f}% chance of surviving 6 months. "
            f"This is the most severe threat identified."
        ),
        "evidence": (
            f"Survival rate: {worst['survival_percentage']:.0f}% "
            f"({worst['survived_count']}/{worst['n_simulations']} simulations)"
        ),
    })

    # Risk 2: Cash reserve adequacy
    runway = metrics["latest_cash_reserve"] / metrics["avg_expenses"] if metrics["avg_expenses"] > 0 else 0
    if runway < 3:
        severity = "Critical"
    elif runway < 6:
        severity = "High"
    else:
        severity = "Medium"

    risks.append({
        "risk_name": "Insufficient Cash Runway",
        "severity": severity,
        "explanation": (
            f"Current cash reserves of ₹{metrics['latest_cash_reserve']:,.0f} provide only "
            f"{runway:.1f} months of operating expenses coverage. "
            f"Industry standard recommends 6+ months."
        ),
        "evidence": (
            f"Cash: ₹{metrics['latest_cash_reserve']:,.0f}, "
            f"Monthly expenses: ₹{metrics['avg_expenses']:,.0f}, "
            f"Runway: {runway:.1f} months"
        ),
    })

    # Risk 3: Profit margin risk
    margin = metrics["avg_profit_margin"]
    risks.append({
        "risk_name": "Thin Profit Margins",
        "severity": "High" if margin < 0.15 else "Medium",
        "explanation": (
            f"Average profit margin of {margin:.1%} leaves limited buffer against "
            f"cost increases. A {metrics['revenue_volatility']:.1%} revenue volatility "
            f"compounds this risk."
        ),
        "evidence": (
            f"Margin: {margin:.1%}, "
            f"Revenue volatility: {metrics['revenue_volatility']:.1%}"
        ),
    })

    return risks


def generate_mock_roadmap(
    metrics: dict[str, Any],
    simulation_results: list[dict[str, Any]],
    risk_analysis: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate deterministic mock financial roadmap (no LLM needed)."""
    sorted_sims = sorted(simulation_results, key=lambda x: x["survival_probability"])
    actions = []

    # Action 1: Cash reserve building
    actions.append({
        "action": "Build emergency cash reserve to cover 6 months of operating expenses",
        "impact": f"Target ₹{metrics['avg_expenses'] * 6:,.0f} in cash reserves",
        "timeline": "3-6 months",
        "priority": 1,
        "category": "Cash Management",
    })

    # Action 2: Address worst shock
    worst = sorted_sims[0]
    actions.append({
        "action": f"Develop contingency plan for {worst['shock_name'].lower()} scenario",
        "impact": f"Improve survival probability from {worst['survival_percentage']:.0f}%",
        "timeline": "2-4 weeks",
        "priority": 2,
        "category": "Risk Mitigation",
    })

    # Action 3: Revenue diversification
    actions.append({
        "action": "Diversify revenue streams to reduce dependency on primary income",
        "impact": f"Reduce revenue volatility from {metrics['revenue_volatility']:.1%}",
        "timeline": "1-3 months",
        "priority": 3,
        "category": "Revenue Growth",
    })

    # Action 4: Cost optimization
    fixed_ratio = metrics["fixed_cost_ratio"]
    actions.append({
        "action": "Review and renegotiate fixed cost contracts (rent, leases, EMIs)",
        "impact": f"Fixed costs are {fixed_ratio:.0%} of expenses — target 40-50%",
        "timeline": "1-2 months",
        "priority": 4,
        "category": "Cost Reduction",
    })

    # Action 5: Operational efficiency
    actions.append({
        "action": "Implement digital invoicing and follow-up to reduce receivables cycle",
        "impact": "Improve cash flow timing by 15-20 days",
        "timeline": "2-3 weeks",
        "priority": 5,
        "category": "Operational Efficiency",
    })

    return actions
