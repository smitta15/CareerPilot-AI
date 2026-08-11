"""
Search Agent - Finds internship opportunities.

Generates optimized search queries and retrieves job listings from Adzuna API.
Handles empty results and API errors gracefully.
"""

from langgraph.types import Command
from app.graph.state import CareerPilotState
from app.graph.navigation import get_next_agent
from app.services.query_service import generate_search_query
from app.services.search_service import search_opportunities
from app.utils.state_validator import StateValidator
from app.logging_config import LoggerFactory
from app.exceptions import SearchError

logger = LoggerFactory.get_logger("careerpilot.agents.search")


def search_agent(state: CareerPilotState) -> Command:
    """
    Search for internship opportunities.

    Generates an optimized search query from user input and profile,
    then queries the Adzuna API for matching jobs.

    Args:
        state: Current CareerPilot state

    Returns:
        Command with opportunities and next agent

    Raises:
        SearchError: If search fails after retries
    """
    logger.info("Starting search agent")

    try:
        # Validate required state
        user_query = StateValidator.get(state, "user_query", required=True)
        profile = StateValidator.get_dict(state, "profile", {})

        logger.debug(f"User query: {user_query}, Profile skills: {profile.get('skills', [])}")

        # Generate optimized search query
        with logger.timer("Query generation"):
            search_request = generate_search_query(user_query, profile)

        optimized_query = search_request.role
        logger.info(f"Generated search query: {optimized_query}")

        # Search opportunities
        with logger.timer("Adzuna API search"):
            jobs = search_opportunities(search_request)

        logger.info(f"Found {len(jobs)} job opportunities")

        if not jobs:
            logger.warning("No jobs found; will continue with empty results")

        # Update state
        state["search_query"] = optimized_query
        state["opportunities"] = jobs or []

        # Mark current step as completed
        StateValidator.validate_required_fields(state, ["execution_plan"])
        if state["execution_plan"] and len(state["execution_plan"]) > state.get("current_step", 0):
            state["execution_plan"][state["current_step"]]["status"] = "completed"
            state["current_step"] = state.get("current_step", 0) + 1

        logger.info("Search agent completed successfully")

        return Command(
            update=state,
            goto=get_next_agent(state)
        )

    except SearchError as e:
        logger.error(f"Search failed: {str(e)}")
        state["error"] = str(e)
        state["opportunities"] = []
        raise

    except Exception as e:
        logger.error(f"Unexpected error in search: {str(e)}", exc_info=True)
        state["error"] = str(e)
        state["opportunities"] = []
        raise SearchError(f"Search agent failed: {str(e)}") from e
