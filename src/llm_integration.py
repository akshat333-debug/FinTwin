"""
LLM Integration Layer for FinTwin.

Supports OpenAI and Google Gemini with graceful fallback to mock responses.
Set OPENAI_API_KEY or GOOGLE_API_KEY environment variable to enable real LLM calls.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

# ── Provider Detection ────────────────────────────────────────────────────────

def _get_provider() -> str | None:
    """Detect which LLM provider is available."""
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("GOOGLE_API_KEY"):
        return "gemini"
    return None


def _extract_json(text: str) -> Any:
    """Extract JSON from LLM response (handles markdown code fences)."""
    # Try to find JSON in code fences
    match = re.search(r'```(?:json)?\s*\n(.*?)```', text, re.DOTALL)
    if match:
        return json.loads(match.group(1).strip())
    # Try to find JSON array or object
    match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    raise ValueError(f"No JSON found in response: {text[:200]}")


# ── OpenAI ────────────────────────────────────────────────────────────────────

def _call_openai(prompt: str, system: str = "You are an expert Indian MSME financial advisor.", temperature: float = 0.3) -> str:
    """Call OpenAI API."""
    from openai import OpenAI
    client = OpenAI()  # Uses OPENAI_API_KEY env var
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=2000,
    )
    return response.choices[0].message.content


# ── Google Gemini ─────────────────────────────────────────────────────────────

def _call_gemini(prompt: str, system: str = "You are an expert Indian MSME financial advisor.", temperature: float = 0.3) -> str:
    """Call Google Gemini API."""
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction=system,
        generation_config={"temperature": temperature, "max_output_tokens": 2000},
    )
    response = model.generate_content(prompt)
    return response.text


# ── Unified Call ──────────────────────────────────────────────────────────────

def call_llm(prompt: str, system: str = "You are an expert Indian MSME financial advisor.", temperature: float = 0.3) -> str:
    """Call whichever LLM provider is available."""
    provider = _get_provider()
    if provider == "openai":
        return _call_openai(prompt, system, temperature)
    elif provider == "gemini":
        return _call_gemini(prompt, system, temperature)
    else:
        raise RuntimeError("No LLM API key found. Set OPENAI_API_KEY or GOOGLE_API_KEY.")


def is_llm_available() -> bool:
    """Check if an LLM provider is configured."""
    return _get_provider() is not None


# ── Public API ────────────────────────────────────────────────────────────────

def generate_llm_risks(
    metrics: dict[str, Any],
    health: dict[str, Any],
    simulation_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate risk analysis using LLM. Falls back to mock if no API key."""
    from src.llm_prompts import build_risk_prompt, generate_mock_risks

    if not is_llm_available():
        return generate_mock_risks(metrics, simulation_results)

    try:
        prompt = build_risk_prompt(metrics, health, simulation_results)
        response = call_llm(prompt)
        risks = _extract_json(response)
        # Validate structure
        for risk in risks:
            assert "risk_name" in risk
            assert "severity" in risk
            assert "explanation" in risk
        return risks[:3]  # Ensure max 3
    except Exception as e:
        print(f"[LLM] Risk generation failed: {e}, falling back to mock")
        return generate_mock_risks(metrics, simulation_results)


def generate_llm_roadmap(
    metrics: dict[str, Any],
    health: dict[str, Any],
    simulation_results: list[dict[str, Any]],
    risks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate financial roadmap using LLM. Falls back to mock if no API key."""
    from src.llm_prompts import build_roadmap_prompt, generate_mock_roadmap

    if not is_llm_available():
        return generate_mock_roadmap(metrics, simulation_results, risks)

    try:
        prompt = build_roadmap_prompt(metrics, health, simulation_results, risks)
        response = call_llm(prompt)
        roadmap = _extract_json(response)
        # Validate structure
        for action in roadmap:
            assert "action" in action
            assert "priority" in action
        return roadmap[:5]  # Ensure max 5
    except Exception as e:
        print(f"[LLM] Roadmap generation failed: {e}, falling back to mock")
        return generate_mock_roadmap(metrics, simulation_results, risks)


def generate_executive_summary(
    metrics: dict[str, Any],
    health: dict[str, Any],
    simulation_results: list[dict[str, Any]],
    forecast: dict[str, Any],
    backtest: list[dict[str, Any]],
) -> str:
    """Generate AI executive summary of the full analysis."""
    from src.llm_prompts import generate_mock_risks

    # Build context
    sim_summary = "\n".join(
        f"- {s['shock_name']}: {s['survival_percentage']:.0f}% survival"
        for s in sorted(simulation_results, key=lambda x: x['survival_probability'])
    )

    backtest_summary = "\n".join(
        f"- {b['event_name']} ({b['year']}): {'Survived' if b['survived'] else 'Failed at M' + str(b['bankruptcy_month'])}, cash change {b['cash_change_pct']}%"
        for b in backtest
    )

    prompt = f"""Write a concise 4-5 sentence EXECUTIVE SUMMARY of this MSME financial analysis.
Be specific with numbers. Write in professional but accessible language.
Do NOT use bullet points — write flowing paragraphs.

## Financial Profile
- Revenue: ₹{metrics['avg_revenue']:,.0f}/month, Profit: ₹{metrics['avg_monthly_profit']:,.0f}/month
- Margin: {metrics['avg_profit_margin']:.1%}, Volatility: {metrics['revenue_volatility']:.1%}
- Cash Reserve: ₹{metrics['latest_cash_reserve']:,.0f}, Burn Rate: ₹{metrics['burn_rate']:,.0f}/month
- Health Score: {health['health_score']}/10 ({health['grade']})

## Stress Test
{sim_summary}

## 6-Month Forecast
- Bankruptcy probability: {forecast['prob_bankrupt_by_end']:.1%}
- Expected cash at end: ₹{forecast['expected_cash_end']:,.0f}

## Historical Resilience
{backtest_summary}

Write the summary now. Be specific, cite numbers, and provide actionable insight:"""

    if not is_llm_available():
        # Fallback: generate a template summary
        worst_shock = sorted(simulation_results, key=lambda x: x['survival_probability'])[0]
        failed_events = [b for b in backtest if not b['survived']]
        return (
            f"This MSME demonstrates a {health['grade'].lower()} financial position with a health score of "
            f"{health['health_score']}/10. Average monthly revenue stands at ₹{metrics['avg_revenue']:,.0f} "
            f"with a {metrics['avg_profit_margin']:.1%} profit margin, and cash reserves of ₹{metrics['latest_cash_reserve']:,.0f}. "
            f"Stress testing across 7 shock scenarios reveals the greatest vulnerability to "
            f"{worst_shock['shock_name'].lower()} ({worst_shock['survival_percentage']:.0f}% survival). "
            f"The 6-month cash flow forecast projects {'a low' if forecast['prob_bankrupt_by_end'] < 0.1 else 'a moderate' if forecast['prob_bankrupt_by_end'] < 0.3 else 'a significant'} "
            f"bankruptcy risk of {forecast['prob_bankrupt_by_end']:.1%}, with expected cash of ₹{forecast['expected_cash_end']:,.0f}. "
            f"Historical backtesting shows the business {'would survive all 6 tested economic crises' if not failed_events else f'would fail during {len(failed_events)} of 6 historical crises'}."
        )

    try:
        return call_llm(prompt, temperature=0.4)
    except Exception as e:
        print(f"[LLM] Summary generation failed: {e}")
        return "Executive summary generation failed. Please check your LLM API configuration."


def answer_chat_question(
    question: str,
    metrics: dict[str, Any],
    health: dict[str, Any],
    simulation_results: list[dict[str, Any]],
    forecast: dict[str, Any],
    backtest: list[dict[str, Any]],
    schemes: list[dict[str, Any]],
    active_page: str = "dashboard",
) -> str:
    """Answer a user's question about their financial data using LLM.

    Parameters
    ----------
    active_page : str
        The frontend page the user is currently viewing, used to provide
        context-aware responses and suggestions.
    """

    # Build comprehensive context
    sim_text = "\n".join(
        f"- {s['shock_name']}: {s['survival_percentage']:.0f}% survival ({s['survived_count']}/{s['n_simulations']})"
        for s in simulation_results
    )
    backtest_text = "\n".join(
        f"- {b['event_name']} ({b['year']}): {'Survived' if b['survived'] else 'Failed M' + str(b['bankruptcy_month'])}, cash change: {b['cash_change_pct']}%"
        for b in backtest
    )
    scheme_text = "\n".join(
        f"- {s['name']} (relevance: {s['relevance_score']}%): {s['reason']}"
        for s in schemes[:5]
    )

    context = f"""## MSME Financial Data
- Average Revenue: ₹{metrics['avg_revenue']:,.0f}/month
- Average Profit: ₹{metrics['avg_monthly_profit']:,.0f}/month
- Profit Margin: {metrics['avg_profit_margin']:.1%}
- Revenue Volatility: {metrics['revenue_volatility']:.1%}
- Cash Reserve: ₹{metrics['latest_cash_reserve']:,.0f}
- Burn Rate: ₹{metrics['burn_rate']:,.0f}/month
- Fixed Cost Ratio: {metrics['fixed_cost_ratio']:.1%}
- Health Score: {health['health_score']}/10 ({health['grade']})

## Stress Test Results
{sim_text}

## 6-Month Cash Forecast
- Starting cash: ₹{forecast['starting_cash']:,.0f}
- Expected cash (P50): ₹{forecast['expected_cash_end']:,.0f}
- Bankruptcy probability: {forecast['prob_bankrupt_by_end']:.1%}

## Historical Backtesting
{backtest_text}

## Recommended Schemes
{scheme_text}"""

    # Context-aware page hints
    page_hints = {
        "dashboard": "The user is viewing the main dashboard overview.",
        "forecast": "The user is viewing the 6-month cash flow forecast. Tailor your answer to forecasting and future projections.",
        "backtest": "The user is viewing historical backtesting results. Reference how the business would perform during past crises.",
        "schemes": "The user is viewing government scheme recommendations. Focus on scheme eligibility and benefits.",
        "risks": "The user is viewing risk analysis and roadmap. Focus on risks, mitigations, and action items.",
        "shocks": "The user is viewing shock model definitions. Explain shock impacts and how they are modeled.",
        "upload": "The user is on the Upload CSV page. Help them understand data format and requirements.",
        "synthetic": "The user is configuring synthetic data generation. Guide them on business type selection.",
    }
    page_context = page_hints.get(active_page, "")

    system = f"""You are FinTwin AI, an expert Indian MSME financial advisor chatbot.
Answer the user's question using ONLY the provided financial data and analysis.
Be specific, cite actual numbers from the data, and give actionable advice.
Keep answers concise (3-5 sentences max) unless the user asks for detail.
If the question is about what-if scenarios, use the stress test data to extrapolate.
Format important numbers and metrics clearly.
{page_context}"""

    prompt = f"""{context}

## User Question
{question}

Answer concisely and specifically, referencing the actual numbers above:"""

    if not is_llm_available():
        # Keyword-based fallback
        q = question.lower()
        if any(w in q for w in ['health', 'score', 'rating', 'grade']):
            return f"Your business has a health score of {health['health_score']}/10, graded as **{health['grade']}**. {health['interpretation']}"
        elif any(w in q for w in ['cash', 'reserve', 'runway', 'burn']):
            runway = metrics['latest_cash_reserve'] / metrics['burn_rate'] if metrics['burn_rate'] > 0 else 999
            return f"Current cash reserves are ₹{metrics['latest_cash_reserve']:,.0f} with a burn rate of ₹{metrics['burn_rate']:,.0f}/month, giving approximately {runway:.1f} months of runway. The 6-month forecast shows a {forecast['prob_bankrupt_by_end']:.1%} probability of running out of cash."
        elif any(w in q for w in ['shock', 'stress', 'survive', 'worst']):
            worst = sorted(simulation_results, key=lambda x: x['survival_probability'])[0]
            best = sorted(simulation_results, key=lambda x: -x['survival_probability'])[0]
            return f"Your business is most vulnerable to **{worst['shock_name']}** ({worst['survival_percentage']:.0f}% survival) and most resilient against **{best['shock_name']}** ({best['survival_percentage']:.0f}% survival). Across all 7 shock scenarios, your average survival rate is {sum(s['survival_percentage'] for s in simulation_results)/len(simulation_results):.0f}%."
        elif any(w in q for w in ['scheme', 'government', 'mudra', 'loan', 'subsidy']):
            if schemes:
                top = schemes[0]
                return f"The most relevant scheme for your business is **{top['name']}** (relevance: {top['relevance_score']}%). {top['reason']}. You can apply at {top.get('url', 'the respective government portal')}."
            return "No government schemes matched your financial profile."
        elif any(w in q for w in ['revenue', 'profit', 'margin', 'income']):
            return f"Your average monthly revenue is ₹{metrics['avg_revenue']:,.0f} with a profit margin of {metrics['avg_profit_margin']:.1%}. Monthly profit averages ₹{metrics['avg_monthly_profit']:,.0f}. Revenue volatility is {metrics['revenue_volatility']:.1%}."
        elif any(w in q for w in ['forecast', 'future', 'predict', 'next']):
            return f"The 6-month forecast shows expected cash position of ₹{forecast['expected_cash_end']:,.0f} (median). The optimistic scenario (P90) projects ₹{forecast['p90'][-1]:,.0f}, while the pessimistic case (P10) shows ₹{forecast['p10'][-1]:,.0f}. Bankruptcy probability is {forecast['prob_bankrupt_by_end']:.1%}."
        elif any(w in q for w in ['covid', 'demonet', 'history', 'crisis', 'backtest']):
            survived = sum(1 for b in backtest if b['survived'])
            return f"Your business would survive {survived} out of {len(backtest)} historical crises. " + " ".join(
                f"{'✓' if b['survived'] else '✗'} {b['event_name']} ({b['cash_change_pct']:+.0f}% cash)."
                for b in backtest[:3]
            )
        else:
            return f"Based on your analysis, your business has a health score of {health['health_score']}/10 ({health['grade']}), with ₹{metrics['avg_revenue']:,.0f}/month revenue and {metrics['avg_profit_margin']:.1%} margin. For more specific insights, try asking about your health score, cash position, stress test results, government schemes, or forecast."

    try:
        return call_llm(prompt, system=system, temperature=0.3)
    except Exception as e:
        print(f"[LLM] Chat failed: {e}")
        return "I'm having trouble connecting to the AI service. Please try again or check your API configuration."
