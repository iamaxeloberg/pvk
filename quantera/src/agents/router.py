"""AI Picker / Agent Router - Classifies queries and routes to the appropriate sub-agent."""

import logging
from litellm import completion
from config.settings import settings
from src.utils import read_prompt, get_llm_content

logger = logging.getLogger(__name__)

VALID_AGENTS = {"kpi", "insight", "briefing", "general"}


def classify_query(user_query: str) -> str:
    """Classify a user query to determine which sub-agent should handle it.

    Args:
        user_query: The user's natural language query

    Returns:
        Agent name: 'kpi', 'insight', 'briefing', or 'general'
    """
    prompt = read_prompt("agent_router")

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_query},
    ]

    response = completion(
        model=settings.low_cost_llm_model,
        messages=messages,
        api_key=settings.low_cost_llm_api_key or None,
        api_base=settings.low_cost_llm_api_base or None,
        temperature=0.0,
        max_tokens=16,
    )

    result = get_llm_content(response).lower()

    if result not in VALID_AGENTS:
        logger.warning(f"Router returned invalid agent '{result}', defaulting to 'general'")
        return "general"

    logger.info(f"Query classified as: {result}")
    return result


def route_query(user_query: str, relevant_documents: list[str], agent: str | None = None) -> dict:
    """Route a query to the appropriate sub-agent and return the result.

    Args:
        user_query: The user's natural language query
        relevant_documents: List of Markdown file paths
        agent: Optional agent override. If None, classification is automatic.

    Returns:
        Dict with keys: agent_used, response, relevant_documents
    """
    if agent is None:
        agent = classify_query(user_query)

    if agent == "kpi":
        from src.agents.kpi_agent import extract_kpis, format_kpi_response

        kpi_data = extract_kpis(user_query, relevant_documents)
        response = format_kpi_response(kpi_data)
        return {"agent_used": "kpi", "response": response, "raw_data": kpi_data, "relevant_documents": relevant_documents}

    elif agent == "insight":
        from src.agents.insight_agent import generate_insights

        response = generate_insights(user_query, relevant_documents)
        return {"agent_used": "insight", "response": response, "relevant_documents": relevant_documents}

    elif agent == "briefing":
        from src.agents.briefing_agent import generate_briefing

        response = generate_briefing(user_query, relevant_documents)
        return {"agent_used": "briefing", "response": response, "relevant_documents": relevant_documents}

    else:
        from src.generator import generate_response

        response = generate_response(user_query, relevant_documents)
        return {"agent_used": "general", "response": response, "relevant_documents": relevant_documents}
